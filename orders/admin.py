from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import Order, OrderItem, CourierLog
from .steadfast import SteadfastClient


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_link', 'created_at', 'status', 'amount_input', 'send_to_pathao_col',
        'invoice_col', 'consignment_col', 'delivery_status_col', 'is_flagged_fraud', 'total'
    )
    list_filter = ('status', 'is_flagged_fraud')
    search_fields = ('id', 'name', 'phone', 'reference', 'pathao_order_id')
    readonly_fields = ('double_entry_hash', 'pathao_order_id', 'pathao_status', 'pathao_response', 'pathao_invoice_url')
    actions = ['send_via_pathao', 'refresh_pathao_status', 'force_send_via_pathao']
    change_form_template = 'admin/orders/order/change_form.html'

    def pathao_status_badge(self, obj: Order):
        if obj.pathao_status:
            color = '#16a34a' if obj.pathao_status.lower() in {'delivered', 'completed'} else '#f59e0b'
            return format_html("<span style='padding:.15rem .35rem;border-radius:.35rem;background:{};color:white;font-size:.75rem'>{}</span>", color, obj.pathao_status)
        return '-'
    pathao_status_badge.short_description = 'Steadfast Status'

    # ---- List display helpers matching screenshot ----
    def order_link(self, obj: Order):
        return format_html('<a href="{}">#{} {}</a>', f"/admin/orders/order/{obj.pk}/change/", obj.pk, obj.name)
    order_link.short_description = 'Order'

    def amount_input(self, obj: Order):
        # Inline small input to optionally override COD amount when sending
        return format_html(
            "<input form='send-form-{}' type='number' name='amount' step='0.01' value='{}' style='width:85px' />",
            obj.pk, obj.total
        )
    amount_input.short_description = 'Amount'

    def send_to_pathao_col(self, obj: Order):
        disabled = (obj.is_flagged_fraud or obj.already_sent_to_courier())
        if disabled:
            return format_html("<span class='button disabled'>Send</span>")
        return format_html(
            "<a class='button' href='{url}'>Send</a>",
            url=f"/admin/orders/order/{obj.pk}/send-pathao/",
        )
    send_to_pathao_col.short_description = 'Send to Steadfast'

    def invoice_col(self, obj: Order):
        if not obj.pathao_order_id:
            return '-'  # can't invoice without consignment
        label = 'Generate' if not obj.pathao_invoice_url else 'Open'
        if obj.pathao_invoice_url:
            return format_html("<a class='button' href='{}' target='_blank'>Invoice</a>", obj.pathao_invoice_url)
        return format_html(
            "<a class='button' href='{url}'>Generate</a>",
            url=f"/admin/orders/order/{obj.pk}/generate-invoice/",
        )
    invoice_col.short_description = 'Invoice'

    def consignment_col(self, obj: Order):
        return obj.pathao_order_id or '-'
    consignment_col.short_description = 'Consignment ID'

    def delivery_status_col(self, obj: Order):
        # show refresh button
        if not obj.pathao_order_id:
            return '-'
        return format_html(
            "<a class='button button-success' href='{url}'>Refresh</a> {}",
            self.pathao_status_badge(obj),
            url=f"/admin/orders/order/{obj.pk}/refresh-pathao/",
        )
    delivery_status_col.short_description = 'DeliveryStatus'

    def _build_pathao_payload(self, order: Order) -> dict:
        """Build payload compatible with Steadfast create_order.

        We continue to store results in existing pathao_* fields.
        """
        items = []
        for it in order.items.all():
            items.append({
                'name': str(it.product),
                'quantity': int(it.qty),
                'price': float(it.price),
            })
        defaults = getattr(settings, 'STEADFAST', {}).get('DEFAULTS', {}) or {}
        payload = {
            # Common required fields for Steadfast
            'invoice': str(order.pk),
            'recipient_name': order.name,
            'recipient_phone': order.phone,
            'recipient_address': order.address,
            'cod_amount': float(order.total),
            # Optional helpers
            'note': f"Order #{order.pk}",
            'items': items,
        }
        # Merge defaults if not explicitly provided
        for k, v in defaults.items():
            payload.setdefault(k, v)
        return payload

    def _generate_invoice_pdf(self, order: Order) -> str:
        """Generate a simple invoice PDF and return the public URL.

        File path: MEDIA_ROOT/invoices/order_<id>.pdf
        URL:       MEDIA_URL + invoices/order_<id>.pdf
        """
        invoices_dir = Path(settings.MEDIA_ROOT) / 'invoices'
        invoices_dir.mkdir(parents=True, exist_ok=True)
        filename = f"order_{order.pk}.pdf"
        filepath = invoices_dir / filename

        # Create PDF
        c = canvas.Canvas(str(filepath), pagesize=A4)
        width, height = A4
        y = height - 50

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, f"Invoice - Order #{order.pk}")
        y -= 30

        # Customer details
        c.setFont("Helvetica", 11)
        c.drawString(40, y, f"Name: {order.name}")
        y -= 18
        c.drawString(40, y, f"Phone: {order.phone}")
        y -= 18
        c.drawString(40, y, f"Address: {order.address}")
        y -= 28

        # Courier info
        c.drawString(40, y, f"Consignment: {order.pathao_order_id or '-'}")
        y -= 18
        c.drawString(40, y, f"Courier Status: {order.pathao_status or '-'}")
        y -= 28

        # Items table
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Items")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(40, y, "Product")
        c.drawString(300, y, "Qty")
        c.drawString(360, y, "Price")
        c.drawString(430, y, "Total")
        y -= 15
        c.line(40, y, 530, y)
        y -= 10

        for it in order.items.all():
            if y < 100:
                c.showPage()
                y = height - 50
            total_line = float(it.price) * int(it.qty)
            c.drawString(40, y, str(it.product))
            c.drawRightString(330, y, str(int(it.qty)))
            c.drawRightString(410, y, f"{float(it.price):.2f}")
            c.drawRightString(510, y, f"{total_line:.2f}")
            y -= 16

        y -= 10
        c.line(350, y, 530, y)
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(410, y, "Grand Total:")
        c.drawRightString(510, y, f"{float(order.total):.2f}")

        c.showPage()
        c.save()

        return f"{settings.MEDIA_URL}invoices/{filename}"

    def send_via_pathao(self, request, queryset):
        client = SteadfastClient()
        sent = 0
        for order in queryset.select_related(None).prefetch_related('items'):
            if order.is_flagged_fraud:
                messages.warning(request, f"Order #{order.pk} is flagged for fraud: {order.fraud_reason or ''}. Skipped.")
                continue
            if order.already_sent_to_courier():
                messages.info(request, f"Order #{order.pk} already has Consignment ID {order.pathao_order_id}. Skipped.")
                continue
            try:
                payload = self._build_pathao_payload(order)
                resp = client.create_order(payload)
                order.pathao_response = resp
                # Extract identifiers from various possible response shapes
                data = resp.get('data') or {}
                order.pathao_order_id = (
                    resp.get('consignment_id')
                    or resp.get('tracking_code')
                    or resp.get('order_id')
                    or data.get('consignment_id')
                    or data.get('consignmentId')
                    or data.get('tracking_code')
                    or data.get('trackingCode')
                )
                order.pathao_status = (
                    resp.get('status')
                    or data.get('status')
                    or resp.get('message')  # sometimes message conveys state
                )
                order.save(update_fields=['pathao_response', 'pathao_order_id', 'pathao_status'])
                CourierLog.objects.create(order=order, action='create', raw_payload=resp)
                sent += 1
            except Exception as e:
                CourierLog.objects.create(order=order, action='error', raw_payload={'error': str(e)})
                messages.error(request, f"Failed to send Order #{order.pk} to Steadfast: {e}")
        if sent:
            messages.success(request, f"Sent {sent} order(s) to Steadfast.")
    send_via_pathao.short_description = "Send via Steadfast"

    def refresh_pathao_status(self, request, queryset):
        client = SteadfastClient()
        updated = 0
        for order in queryset:
            if not order.pathao_order_id:
                messages.info(request, f"Order #{order.pk} has no consignment ID. Skipped.")
                continue
            try:
                resp = client.get_order_status(order.pathao_order_id)
                status = resp.get('status') or resp.get('data', {}).get('status')
                order.pathao_status = status
                order.pathao_response = resp
                order.save(update_fields=['pathao_status', 'pathao_response'])
                CourierLog.objects.create(order=order, action='status', raw_payload=resp)
                updated += 1
            except Exception as e:
                CourierLog.objects.create(order=order, action='error', raw_payload={'error': str(e)})
                messages.error(request, f"Failed to refresh Order #{order.pk} status: {e}")
        if updated:
            messages.success(request, f"Updated {updated} order(s) from Steadfast.")
    refresh_pathao_status.short_description = "Refresh Steadfast Status"

    def force_send_via_pathao(self, request, queryset):
        """Bypass fraud flag and send anyway (manual override)."""
        client = SteadfastClient()
        sent = 0
        for order in queryset.select_related(None).prefetch_related('items'):
            if order.already_sent_to_courier():
                messages.info(request, f"Order #{order.pk} already has Consignment ID {order.pathao_order_id}. Skipped.")
                continue
            try:
                payload = self._build_pathao_payload(order)
                resp = client.create_order(payload)
                order.pathao_response = resp
                order.pathao_order_id = (
                    resp.get('consignment_id')
                    or resp.get('tracking_code')
                    or resp.get('order_id')
                    or resp.get('data', {}).get('consignment_id')
                )
                order.pathao_status = resp.get('status') or resp.get('data', {}).get('status')
                order.save(update_fields=['pathao_response', 'pathao_order_id', 'pathao_status'])
                CourierLog.objects.create(order=order, action='create', raw_payload=resp)
                sent += 1
            except Exception as e:
                CourierLog.objects.create(order=order, action='error', raw_payload={'error': str(e)})
                messages.error(request, f"Failed to FORCE send Order #{order.pk} to Steadfast: {e}")
        if sent:
            messages.success(request, f"Force-sent {sent} order(s) to Steadfast.")
    force_send_via_pathao.short_description = "Force Send via Steadfast (Override Fraud)"

    # ---- Per-object buttons (change form) ----
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:order_id>/send-pathao/', self.admin_site.admin_view(self.view_send_single), name='orders_order_send_pathao'),
            path('<int:order_id>/force-send-pathao/', self.admin_site.admin_view(self.view_force_send_single), name='orders_order_force_send_pathao'),
            path('<int:order_id>/refresh-pathao/', self.admin_site.admin_view(self.view_refresh_single), name='orders_order_refresh_pathao'),
            path('<int:order_id>/toggle-fraud/', self.admin_site.admin_view(self.view_toggle_fraud), name='orders_order_toggle_fraud'),
            path('<int:order_id>/generate-invoice/', self.admin_site.admin_view(self.view_generate_invoice), name='orders_order_generate_invoice'),
        ]
        return custom + urls

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context = context or {}
        context.setdefault('show_send_pathao', bool(obj and not obj.is_flagged_fraud and not obj.already_sent_to_courier()))
        context.setdefault('show_force_send', bool(obj and not obj.already_sent_to_courier()))
        context.setdefault('show_refresh_status', bool(obj and obj.already_sent_to_courier()))
        context.setdefault('fraud_flag', bool(obj and obj.is_flagged_fraud))
        return super().render_change_form(request, context, add, change, form_url, obj)

    def view_send_single(self, request, order_id):
        order = get_object_or_404(self.model, pk=order_id)
        if order.is_flagged_fraud:
            messages.warning(request, "Order is flagged as fraud. Use Force Send to override.")
            return redirect(request.META.get('HTTP_REFERER', '..'))
        if order.already_sent_to_courier():
            messages.info(request, "Order already sent to Pathao.")
            return redirect(request.META.get('HTTP_REFERER', '..'))
        client = SteadfastClient()
        try:
            # optional amount override
            amount_override = request.POST.get('amount')
            payload = self._build_pathao_payload(order)
            if amount_override:
                try:
                    payload['cod_amount'] = float(amount_override)
                except Exception:
                    pass
            resp = client.create_order(payload)
            order.pathao_response = resp
            data = resp.get('data') or {}
            order.pathao_order_id = (
                resp.get('consignment_id')
                or resp.get('tracking_code')
                or resp.get('order_id')
                or data.get('consignment_id')
                or data.get('consignmentId')
                or data.get('tracking_code')
                or data.get('trackingCode')
            )
            order.pathao_status = (
                resp.get('status')
                or data.get('status')
                or resp.get('message')
            )
            order.save(update_fields=['pathao_response', 'pathao_order_id', 'pathao_status'])
            CourierLog.objects.create(order=order, action='create', raw_payload=resp)
            messages.success(request, "Sent to Steadfast.")
        except Exception as e:
            CourierLog.objects.create(order=order, action='error', raw_payload={'error': str(e)})
            messages.error(request, f"Failed to send: {e}")
        return redirect(request.META.get('HTTP_REFERER', '..'))

    def view_force_send_single(self, request, order_id):
        order = get_object_or_404(self.model, pk=order_id)
        if order.already_sent_to_courier():
            messages.info(request, "Order already sent to Pathao.")
            return redirect(request.META.get('HTTP_REFERER', '..'))
        client = SteadfastClient()
        try:
            resp = client.create_order(self._build_pathao_payload(order))
            order.pathao_response = resp
            order.pathao_order_id = (
                resp.get('consignment_id')
                or resp.get('tracking_code')
                or resp.get('order_id')
                or resp.get('data', {}).get('consignment_id')
            )
            order.pathao_status = resp.get('status') or resp.get('data', {}).get('status')
            order.save(update_fields=['pathao_response', 'pathao_order_id', 'pathao_status'])
            CourierLog.objects.create(order=order, action='create', raw_payload=resp)
            messages.success(request, "Force-sent to Steadfast.")
        except Exception as e:
            CourierLog.objects.create(order=order, action='error', raw_payload={'error': str(e)})
            messages.error(request, f"Failed to force send: {e}")
        return redirect(request.META.get('HTTP_REFERER', '..'))

    def view_refresh_single(self, request, order_id):
        order = get_object_or_404(self.model, pk=order_id)
        if not order.pathao_order_id:
            messages.info(request, "No Pathao order ID to refresh.")
            return redirect(request.META.get('HTTP_REFERER', '..'))
        client = SteadfastClient()
        try:
            resp = client.get_order_status(order.pathao_order_id)
            order.pathao_status = resp.get('status') or resp.get('data', {}).get('status')
            order.pathao_response = resp
            order.save(update_fields=['pathao_status', 'pathao_response'])
            CourierLog.objects.create(order=order, action='status', raw_payload=resp)
            messages.success(request, "Status refreshed.")
        except Exception as e:
            CourierLog.objects.create(order=order, action='error', raw_payload={'error': str(e)})
            messages.error(request, f"Failed to refresh: {e}")
        return redirect(request.META.get('HTTP_REFERER', '..'))

    def view_toggle_fraud(self, request, order_id):
        order = get_object_or_404(self.model, pk=order_id)
        order.is_flagged_fraud = not order.is_flagged_fraud
        order.save(update_fields=['is_flagged_fraud'])
        state = 'ON' if order.is_flagged_fraud else 'OFF'
        messages.success(request, f"Fraud flag toggled {state}.")
        return redirect(request.META.get('HTTP_REFERER', '..'))

    def view_generate_invoice(self, request, order_id):
        """Generate or fetch Pathao invoice for a consignment and store URL."""
        order = get_object_or_404(self.model, pk=order_id)
        if not order.pathao_order_id:
            messages.info(request, "No Pathao order ID; send to Pathao first.")
            return redirect(request.META.get('HTTP_REFERER', '..'))
        client = SteadfastClient()
        try:
            # Generate local PDF invoice
            invoice_url = self._generate_invoice_pdf(order)
            order.pathao_invoice_url = invoice_url
            order.save(update_fields=['pathao_invoice_url'])
            messages.success(request, "Invoice generated.")
            CourierLog.objects.create(order=order, action='invoice', raw_payload={'invoice_url': invoice_url})
        except Exception as e:
            CourierLog.objects.create(order=order, action='error', raw_payload={'error': str(e)})
            messages.error(request, f"Invoice failed: {e}")
        return redirect(request.META.get('HTTP_REFERER', '..'))


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'qty', 'price')


@admin.register(CourierLog)
class CourierLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'action', 'created_at')
    readonly_fields = ('order', 'action', 'raw_payload', 'created_at')
