from PIL import Image
import colorsys
import math
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

GETTING_RESOLUTION = 0
GETTING_COLOR = 1
CALCULATING = 2

def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Привет, {first_name}! Готов увидеть нечто прекрасное?")
    start_getting_info(update, context)

def start_getting_info(update, context):
    context.user_data['STATE'] = GETTING_RESOLUTION
    update.message.reply_text(f"Если да, то напиши мне разрешение будущей картинки")

def received_resolution(update, context):
    try:
        resolution = int(update.message.text)
        if resolution > 1000:
            raise ValueError("invalid value")

        context.user_data['resolution'] = resolution
        update.message.reply_text(
            f"А также цвет множества")
        context.user_data['STATE'] = GETTING_COLOR
    except:
        update.message.reply_text(
            "it's funny but it doesn't seem to be correct...")

def received_color(update, context):
    context.user_data['color'] = update.message.text
    update.message.reply_text(f"Замечательно! И поехали...")
    context.user_data['STATE'] = CALCULATING
    draw(update, context)

def draw(update, context):
    color = context.user_data['color']
    width = context.user_data['resolution']
    x = -0.65
    y = 0
    xRange = 3.4
    aspectRatio = 4 / 3

    precision = 100

    height = round(width / aspectRatio)
    yRange = xRange / aspectRatio
    minX = x - xRange / 2
    maxX = x + xRange / 2
    minY = y - yRange / 2
    maxY = y + yRange / 2

    img = Image.new('RGB', (width, height), color=color)
    pixels = img.load()

    def logColor(distance, base, const, scale):
        color = -1 * math.log(distance, base)
        rgb = colorsys.hsv_to_rgb(const + scale * color, 0.8, 0.9)
        return tuple(round(i * 255) for i in rgb)

    def powerColor(distance, exp, const, scale):
        color = distance ** exp
        rgb = colorsys.hsv_to_rgb(const + scale * color, 1 - 0.6 * color, 0.9)
        return tuple(round(i * 255) for i in rgb)

    for row in range(height):
        for col in range(width):
            x = minX + col * xRange / width
            y = maxY - row * yRange / height
            oldX = x
            oldY = y
            for i in range(precision + 1):
                a = x * x - y * y
                b = 2 * x * y
                x = a + oldX
                y = b + oldY
                if x * x + y * y > 4:
                    break
            if i < precision:
                distance = (i + 1) / (precision + 1)
                rgb = powerColor(distance, 0.2, 0.27, 1.0)
                pixels[col, row] = rgb
            index = row * width + col + 1
            print("{} / {}, {}%".format(index, width * height, round(index / width / height * 100 * 10) / 10))

    img.save(f'{update.message.chat_id}.png')
    context.bot.send_photo(update.message.chat_id, photo=open(f'{update.message.chat_id}.png', 'rb'))
    context.user_data['STATE'] = GETTING_RESOLUTION

def help(update, context):
    update.message.reply_text('Для начала работы набери команду /start')

def error(update, context):
    update.message.reply_text('Кажется, что-то пошло не так. Для помощи набери команду /help')

def text(update, context):
    global STATE

    if context.user_data['STATE'] is None:
        pass

    if context.user_data['STATE'] == GETTING_RESOLUTION:
        return received_resolution(update, context)

    if context.user_data['STATE'] == GETTING_COLOR:
        return received_color(update, context)

    if context.user_data['STATE'] == CALCULATING:
        update.message.reply_text(f"Picture is calculating")

def main():
    TOKEN = "2134931651:AAHRUjMB94emT6mIqROVKD9Mrr-rLZCl_ug"

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))

    dispatcher.add_handler(MessageHandler(Filters.text, text))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()