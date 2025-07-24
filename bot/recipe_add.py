import sqlite3
from openpyxl import load_workbook as lw

try:
    d = lw('recipes_list.xlsx')    
except: 
    print("Файл не найден")
    sys.exit()
    
data = d.active    

conn = sqlite3.connect('recipe.sqlite')
cur = conn.cursor()

# для каждой строки файла, начиная со второй линии достаем соответствующие элементы
for line in data.iter_rows(min_row=2, values_only=True):
    
    recipe = line[0].strip()
    product = line[1].strip().split(';') #очищаем от лишних пробелов и делим продукты 
    des = line[2].strip()
    
    cur.execute('INSERT OR IGNORE INTO Recipes (name, description) VALUES (?, ?)', (recipe, des))
    cur.execute('SELECT id FROM Recipes WHERE name = ?', (recipe,))
    recipe_id = cur.fetchone()[0]
    
#обрабатываем каждый продукт, удаляем пробелы и приводим в нижний регистр
    for prod in product:
        prod = prod.strip().lower()
        if not prod: continue
        
        cur.execute('INSERT OR IGNORE INTO Products (name) VALUES (?)', (prod,))
        cur.execute('SELECT id FROM Products WHERE name = ?', (prod,))
        product_id = cur.fetchone()[0]
        
        cur.execute('INSERT OR IGNORE INTO RP (recipe_id, product_id) VALUES (?, ?)', (recipe_id, product_id))

conn.commit()
conn.close()

print("Новые рецепты добавлены в базу!")