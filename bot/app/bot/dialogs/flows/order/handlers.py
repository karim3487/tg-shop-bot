import logging

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from app.bot.dialogs.flows.order.states import OrderSG
from app.bot.order_notifier import AdminNotifierService
from app.bot.services.order import OrderService
from app.infrastructure.database.db import DB
from app.infrastructure.database.models.client import ClientModel

logger = logging.getLogger(__name__)


async def on_full_name(
    message: Message, widget: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["full_name"] = value.strip()
    await manager.switch_to(OrderSG.address)


async def on_address(
    message: Message, widget: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["address"] = value.strip()
    await manager.switch_to(OrderSG.confirm)


async def on_confirm(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    db: DB = manager.middleware_data["db"]
    db_pool = manager.middleware_data["db_pool"]
    bot: Bot = manager.middleware_data["bot"]
    client: ClientModel | None = manager.middleware_data.get("client")

    if not client:
        await callback.answer("Сначала нажми /start", show_alert=True)
        return

    data = manager.dialog_data
    order_service = OrderService(db_pool)

    try:
        # Step 3: Extract Business Services & UoW
        # The checkout process is now atomic and encapsulated in a service
        order = await order_service.checkout(
            client_id=client.id,
            full_name=data["full_name"],
            phone=client.phone or "",
            address=data["address"],
        )
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
        await manager.done()
        return
    except Exception as e:
        logger.exception("Checkout failed for client %s: %s", client.id, e)
        await callback.answer("Ошибка при создании заказа. Попробуйте позже.", show_alert=True)
        return

    # Step 4: Fix Handlers & Telegram API
    # Notification happens STRICTLY AFTER the DB transaction is committed and returned to the pool
    notifier = AdminNotifierService(bot)
    await notifier.notify_new_order(db, order.id)

    # Store order info for the payment window
    # Fetch items from the order (since cart is already cleared)
    order_items = await db.orders.get_items(order_id=order.id)
    items_text = "\n".join(
        f"  • {i.product_name} × {i.quantity} = {i.subtotal} ₽" 
        for i in order_items
    )

    manager.dialog_data["order_id"] = order.id
    manager.dialog_data["order_total"] = str(order.total_price)
    manager.dialog_data["order_items_text"] = items_text

    await manager.switch_to(OrderSG.payment)


async def on_paid(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    db: DB = manager.middleware_data["db"]
    bot: Bot = manager.middleware_data["bot"]
    order_id = int(manager.dialog_data["order_id"])

    await db.orders.update_status(order_id=order_id, status="paid", expected_old_status="pending")

    # Notify admin that payment received
    admin_chat_id = await db.settings.get_admin_chat_id()
    if admin_chat_id:
        try:
            await bot.send_message(
                chat_id=admin_chat_id,
                text=f"💰 <b>Заказ #{order_id} оплачен!</b>",
            )
        except Exception as e:
            logger.warning("Failed to notify admin about payment: %s", e)

    await manager.done()
    await callback.message.answer(
        f"🎉 <b>Оплата подтверждена!</b>\n\n"
        f"Заказ <b>#{order_id}</b> принят в обработку.\n"
        "Мы свяжемся с вами в ближайшее время. Спасибо! 🙏"
    )


async def on_cancel(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.done()
    await callback.message.answer("❌ Оформление заказа отменено.")


async def on_cancel_order(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    """Cancel an already-created order from the payment screen."""
    db: DB = manager.middleware_data["db"]
    order_id = int(manager.dialog_data.get("order_id", 0))
    if order_id:
        await db.orders.update_status(
            order_id=order_id, 
            status="cancelled", 
            expected_old_status="pending"
        )

    await manager.done()
    await callback.message.answer(f"❌ Заказ #{order_id} отменён.")
