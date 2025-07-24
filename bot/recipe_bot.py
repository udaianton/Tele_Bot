import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
#import pdb
#pdb.set_trace()
# приветственная команда, обращающаяся по имени
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f'Привет, {user_name}! Из чего хочешь сегодня готовить? Напиши один продукт.')

# прием и обработка текстового сообщения от пользователя (введенного продукта)
async def user_product (update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    
    conn = sqlite3.connect('recipe.sqlite')
    cur = conn.cursor()
    
    cur.execute('SELECT id FROM Products WHERE name = ?', (user_input,))
    result = cur.fetchone()
    
    if not result:
        await update.message.reply_text('Рецептов с таким продуктом не найдено. Или попробуйте: написать в единственном числе (помидор, а не помидоры), проверить на ошибки, убедиться, что продукт написан на русском языке.')
        conn.close()
        return
    
    product_id = result[0]
    
    cur.execute('''
        SELECT Recipes.id, Recipes.name, Recipes.description
        FROM Recipes
        JOIN RP ON Recipes.id = RP.recipe_id
        WHERE RP.product_id = ?
    ''', (product_id,))
    recipes = cur.fetchall()
    conn.close()
    
    if not recipes:
        await update.message.reply_text('Рецептов с таким продуктом не найдено. Или попробуйте: написать в единственном числе (помидор, а не помидоры), проверить на ошибки, убедиться, что продукт написан на русском языке.')
        conn.close()
        return
    
    print (recipes)
    
#Создаю интерактивные кнопки

    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"recipe_{recipe_id}")]
        for recipe_id, name, description in recipes
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        f'Найденых рецептов с продуктом "{user_input}" = {len(recipes)}:',
        reply_markup=reply_markup
    )
# конец создания кнопки

# пользователь тыкает на кнопку с нужным рецептом
async def recipe_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("recipe_"):
        return

    recipe_id = int(data.split("_")[1])

    conn = sqlite3.connect('recipe.sqlite')
    cur = conn.cursor()

    cur.execute('SELECT name, description FROM Recipes WHERE id = ?', (recipe_id,))
    result = cur.fetchone()
    if not result:
        await query.edit_message_text("Рецепт не найден.")
        return

    name, description = result

    cur.execute('''
        SELECT Products.name
        FROM Products
        JOIN RP ON Products.id = RP.product_id
        WHERE RP.recipe_id = ?
    ''', (recipe_id,))
    ingredients = [row[0] for row in cur.fetchall()]
    conn.close()

    ingredients_text = ', '.join(ingredients)
        
    text = (
        f'<b>{name}</b>\n'
        f'Ингредиенты: {ingredients_text}\n'
        f'Как готовить: <i>{description}</i>\n\n'
    )
    
    await query.edit_message_text(text, parse_mode='HTML')

TOKEN = '7867254524:AAEiHqMZmnbrm-g2KowVzPgKKI50hat5Mbo'

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_product))
    app.add_handler(CallbackQueryHandler(recipe_detail))
    
    print('Бот запущен в ТГ')
    app.run_polling()
    
if __name__ == '__main__':
    main()
