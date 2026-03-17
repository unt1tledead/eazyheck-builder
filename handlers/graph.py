from aiogram import Router
from aiogram.types import Message, FSInputFile, InputMediaPhoto
import psutil, asyncio, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tempfile, os

router = Router()
graph_state = {"active": False, "stop": False}

def make_graph(cpu_data, ram_data):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), facecolor="#1e1e1e")
    for ax in (ax1, ax2):
        ax.set_facecolor("#2b2b2b")
        ax.tick_params(colors="white")
        ax.spines[:].set_color("#444")
    ax1.plot(cpu_data, color="#00bfff", linewidth=2)
    ax1.set_title("CPU %", color="white")
    ax1.set_ylim(0, 100)
    ax1.fill_between(range(len(cpu_data)), cpu_data, alpha=0.2, color="#00bfff")
    ax2.plot(ram_data, color="#ff6b6b", linewidth=2)
    ax2.set_title("RAM %", color="white")
    ax2.set_ylim(0, 100)
    ax2.fill_between(range(len(ram_data)), ram_data, alpha=0.2, color="#ff6b6b")
    plt.tight_layout(pad=2)
    path = tempfile.mktemp(suffix=".png")
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close()
    return path

@router.message(lambda m: m.text == "📊 График")
async def start_graph(message: Message, bot):
    if graph_state["active"]:
        await message.answer("⚠️ График уже активен. /stopgraph — остановить.")
        return
    graph_state["active"] = True
    graph_state["stop"] = False
    cpu_data, ram_data = [], []
    for _ in range(3):
        cpu_data.append(psutil.cpu_percent(interval=0.5))
        ram_data.append(psutil.virtual_memory().percent)
    path = make_graph(cpu_data, ram_data)
    sent = await message.answer_photo(
        FSInputFile(path),
        caption="📊 Живой график (обновляется каждые 3 сек)\n/stopgraph — остановить"
    )
    os.remove(path)
    msg_id = sent.message_id
    chat_id = message.chat.id

    async def update_loop():
        while not graph_state["stop"]:
            await asyncio.sleep(3)
            if graph_state["stop"]:
                break
            cpu_data.append(psutil.cpu_percent(interval=0.5))
            ram_data.append(psutil.virtual_memory().percent)
            if len(cpu_data) > 30:
                cpu_data.pop(0)
                ram_data.pop(0)
            path = make_graph(cpu_data, ram_data)
            try:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=msg_id,
                    media=InputMediaPhoto(media=FSInputFile(path))
                )
            except Exception:
                pass
            finally:
                if os.path.exists(path):
                    os.remove(path)
        graph_state["active"] = False

    asyncio.create_task(update_loop())

@router.message(lambda m: m.text == "/stopgraph")
async def stop_graph(message: Message):
    if not graph_state["active"]:
        await message.answer("❌ График не запущен")
        return
    graph_state["stop"] = True
    await message.answer("⏹ График остановлен")
