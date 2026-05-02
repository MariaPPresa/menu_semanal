"""
Base de datos de recetas.
Edita este archivo para anadir tus propias recetas.

Temporadas: primavera, verano, otono, invierno, todas
            Tambien puede ser una lista: [primavera, verano]
Horas: desayuno, comida, cena, todas o lista: [comida, cena]
Categorias: pasta_arroz, legumbres, pescado_azul, pescado_blanco,
            carne_blanca, carne_roja, ensalada, verdura
Tipo: completo, acompanamiento, segundo

NO incluyas aceite de oliva en ingredientes.
"""


class Receta:
    def __init__(self, nombre, categoria, ingredientes, temporada="todas", hora="comida", tipo="completo", fritura=False, raciones=1):
        self.nombre = nombre
        self.categoria = categoria
        self.ingredientes = ingredientes
        self.temporada = temporada
        self.hora = hora
        self.tipo = tipo
        self.fritura = fritura
        self.raciones = raciones

    def en_temporada(self, temp):
        if self.temporada == "todas":
            return True
        if isinstance(self.temporada, list):
            return temp in self.temporada
        return self.temporada == temp

    def en_hora(self, h):
        """Comprueba si la receta es valida para una hora dada."""
        if self.hora == "todas":
            return True
        if isinstance(self.hora, list):
            return h in self.hora
        return self.hora == h

    def lleva_huevo(self):
        return "huevo" in self.ingredientes


RECETAS = [
    # --- PASTA/ARROZ ---
    Receta("Fideos chinos", "pasta_arroz", ["pasta", "calabacin", "pimiento", "tomate", "ajo", "cebolla"], "todas", "comida"),
    Receta("Arroz con pollo y verduras", "pasta_arroz", ["arroz", "pollo", "pimiento", "cebolla", "zanahoria"], "todas", "comida", raciones=2),
    Receta("Pasta carbonara", "pasta_arroz", ["pasta", "huevo", "queso"], "todas", "comida"),
    Receta("Arroz blanco con huevo y salchicha", "pasta_arroz", ["arroz", "huevo", "salchicha"], "todas", "comida"),
    Receta("Pasta con picadillo", "pasta_arroz", ["pasta", "picadillo", "tomate frito"], "todas", "comida"),
    Receta("Pasta bolonesa", "pasta_arroz", ["pasta", "carne picada", "tomate frito"], "todas", "comida"),
    Receta("Fideua", "pasta_arroz", ["fideua", "atun en lata", "gambas", "sepia", "caldo de marisco", "mejillones", "cebolla", "pimiento", "ajo"], "todas", "comida", raciones=2),
    Receta("Paella", "pasta_arroz", ["arroz", "gambas", "ajo", "pimiento", "cebolla", "sepia", "mejillones", "caldo de marisco"], "todas", "comida", raciones=2),
    Receta("Paella de carne", "pasta_arroz", ["arroz", "pimiento", "costillas de cerdo", "cebolla", "ajo", "pollo", "caldo de carne"], "todas", "comida", raciones=2),
    Receta("Espaguetis con zamburinas", "pasta_arroz", ["pasta", "zamburinas en lata"], "todas", "comida"),

    # --- LEGUMBRES ---
    Receta("Lentejas", "legumbres", ["lentejas", "zanahoria", "patata", "cebolla", "ajo", "pimiento", "jamon", "chorizo"], ["otono", "invierno", "primavera"], "comida", raciones=2),
    Receta("Garbanzos con bacalao y espinacas", "legumbres", ["garbanzos", "espinacas", "bacalao", "patata", "zanahoria", "tomate frito", "cebolla", "pimiento"], ["otono", "invierno", "primavera"], "comida", raciones=2),
    Receta("Fabes", "legumbres", ["fabes", "lacon", "tocino", "morcilla asturiana", "chorizo"], ["otono", "invierno"], "comida", raciones=2),
    Receta("Guisantes con jamon", "legumbres", ["guisantes", "jamon", "cebolla"], ["primavera", "verano"], "comida", "acompanamiento"),
    Receta("Garbanzos con chorizo", "legumbres", ["garbanzos", "chorizo"], "todas", "comida"),
    Receta("Garbanzos con vinagreta", "legumbres", ["garbanzos", "huevo", "pimiento piquillo", "pepinillo", "cebolla"], ["primavera", "verano"], "comida"),
    Receta("Garbanzos con curry", "legumbres", ["garbanzos", "curry", "nata", "cebolla", "zanahoria", "pimiento", "pollo"], "todas", "comida", raciones=2),
    Receta("Arroz con curry", "pasta_arroz", ["arroz", "curry", "nata", "cebolla", "zanahoria", "pimiento", "pollo"], "todas", "comida", raciones=2),
    Receta("Fabes pintes", "legumbres", ["fabes pintes", "zanahoria", "patata", "cebolla", "pimiento", "jamon", "chorizo"], ["otono", "invierno", "primavera"], "comida", raciones=2),

    # --- PESCADO AZUL ---
    Receta("Salmon al horno", "pescado_azul", ["salmon", "cebolla", "patata", "ajo", "limon"], "todas", "comida"),
    Receta("Salmon a la plancha", "pescado_azul", ["salmon", "limon"], "todas", ["comida", "cena"], "segundo"),
    Receta("Atun a la plancha", "pescado_azul", ["atun suprema", "limon", "ajo"], "todas", ["comida", "cena"], "segundo"),
    
    # --- PESCADO BLANCO ---
    Receta("Dorada al horno", "pescado_blanco", ["dorada", "patata", "cebolla", "ajo", "limon"], "todas", "comida"),
    Receta("Lubina al horno", "pescado_blanco", ["lubina", "patata", "cebolla", "ajo",], "todas", "comida"),
    Receta("Dorada a la plancha", "pescado_azul", ["dorada", "limon"], "todas", ["comida", "cena"], "segundo"),
    Receta("Lubina a la plancha", "pescado_azul", ["lubina", "limon"], "todas", ["comida", "cena"], "segundo"),
    Receta("Bacalao con tomate", "pescado_blanco", ["bacalao", "guisantes", "salsa de tomate", "pimiento", "cebolla", "ajo"], "todas", ["comida", "cena"]),
    Receta("Gambas al ajillo", "pescado_blanco", ["gambas", "ajo", "limon"], "todas", "cena", "segundo"),

    # --- CARNE BLANCA ---
    Receta("Pollo al horno", "carne_blanca", ["pollo", "cebolla", "ajo"], "todas", "comida", "segundo"),
    Receta("Pavo a la plancha", "carne_blanca", ["solomillo de pavo"], "todas", ["comida", "cena"], "segundo"),
    Receta("Pechuga de pollo a la plancha", "carne_blanca", ["pollo"], "todas", ["comida", "cena"], "segundo"),
    Receta("Solomillo de cerdo", "carne_blanca", ["solomillo de cerdo"], "todas", ["comida", "cena"], "segundo"),
    Receta("Lomo", "carne_blanca", ["lomo"], "todas", ["comida", "cena"], "segundo"),
    Receta("Lacón con patatas", "carne_blanca", ["lacón cocido", "patata"], "todas", ["comida", "cena"]),
    Receta("Chuletas de cerdo", "carne_blanca", ["chuletas de cerdo"], "todas", ["comida", "cena"], "segundo"),
    Receta("Costillas al horno", "carne_blanca", ["costillar de cerdo"], "todas", "comida", "segundo"),

    # --- CARNE ROJA ---
    Receta("Filete de ternera", "carne_roja", ["filete de ternera"], "todas", ["comida", "cena"], "segundo"),
    Receta("Estofado de ternera", "carne_roja", ["tacos de ternera", "patata", "zanahoria", "cebolla", "ajo", "vino tinto", "pimiento"], ["otono", "invierno"], "comida", raciones=2),
    Receta("Chuletillas de cordero", "carne_blanca", ["chuletillas de cordero"], "todas", ["comida", "cena"], "segundo"),

    # --- PLATOS CON HUEVO ---
    Receta("Tortilla de patata", "fritura", ["huevo", "patata", "cebolla"], "todas", "cena"),
    Receta("Revuelto de jamon", "carne_blanca", ["huevo", "jamon"], "todas", "cena"),
    Receta("Tortilla de espinacas", "verdura", ["huevo", "espinacas", "cebolla"], "todas", "cena", "acompañamiento"),
    Receta("Revuelto de champinones", "verdura", ["huevo", "champinones", "ajo"], ["otono", "invierno"], "cena"),
    Receta("Huevos rotos con patata y morcilla", "fritura", ["huevo", "morcilla de arroz", "patata"], "todas", "cena"),
    Receta("Huevos rotos con patata y butifarra", "fritura", ["huevo", "butifarra", "patata"], "todas", "cena"),
    Receta("Huevos rotos con patata y chistorra", "fritura", ["huevo", "chistorra", "patata"], "todas", "cena"),
    Receta("Huevo a la plancha", "verdura", ["huevo"], "todas", ["comida", "cena"], "acompanamiento"),
    
    # --- ENSALADA ---
    Receta("Ensalada mixta", "ensalada", ["lechuga", "tomate", "pepinillo", "cebolla"], "todas", ["comida","cena"], "acompanamiento"),
    Receta("Salmorejo", "ensalada", ["tomate", "ajo", "jamon", "huevo", "pan"], "verano", ["comida","cena"], "acompanamiento"),
    Receta("Ensalada campera", "ensalada", ["patata", "pepinillo", "cebolla", "tomate", "atun en lata"], ["primavera", "verano"], ["comida","cena"]),
    Receta("Ensalada templada", "ensalada", ["lechuga", "gula", "pimiento", "cebolla", "tomate"], ["primavera", "verano"], "cena"),

    # --- VERDURA COCINADA ---
    Receta("Crema de calabacin", "verdura", ["calabacin", "patata", "cebolla", "patata", "puerro", "zanahoria"], ["otono", "invierno"], ["comida","cena"], "acompanamiento"),
    Receta("Crema de calabaza", "verdura", ["calabaza", "patata", "cebolla", "puerro"], ["otono", "invierno"], ["comida","cena"], "acompanamiento"),
    Receta("Pisto con huevo", "verdura", ["pimiento", "cebolla", "calabacin", "tomate", "huevo"], "todas", "cena"),
    Receta("Berenjena rellena", "verdura", ["berenjena", "tomate", "cebolla", "pimiento", "queso", "carne picada"], ["otono", "verano"], "comida"),
    Receta("Pimientos a la plancha", "verdura", ["pimiento"], "todas", ["comida","cena"],  "acompanamiento"),
    Receta("Champiñones al ajillo", "verdura", ["champinones", "ajo"], "todas", ["comida","cena"], "acompanamiento"),
    Receta("Esparragos trigueros", "verdura", ["esparragos"], "todas", ["comida","cena"], "acompanamiento"),

    # --- OTROS ---
    Receta("Nuggets", "fritura", ["nuggets"], "todas", "cena", "acompanamiento"),
    Receta("Croquetas", "fritura", ["croquetas"], "todas", "cena", "acompanamiento"),
    Receta("Rollitos primavera", "fritura", ["rollitos primavera"], "todas", "cena", "acompanamiento"),
    Receta("Pizza", "fritura", ["harina", "levadura", "tomate frito", "mozzarella"], "todas", "cena"),
    Receta("Tostas de tomate y mozzarella", "verdura", ["tomate", "mozzarella"], "todas", "cena"),
    Receta("Bocata de lomo", "carne_blanca", ["lomo", "queso", "pimiento"], "todas", "cena"),
    Receta("Empanada de atún", "pescado_azul", ["atun en lata", "pimiento de piquillo", "cebolla", "huevo"], "todas", "cena"),
    Receta("Patata cocida", "verdura", ["patata"], "todas", "acompanamiento"),
    Receta("Patatas fritas", "fritura", ["patata"], "todas", "acompanamiento"),
    Receta("Arroz", "verdura", ["arroz"], "todas", "acompanamiento"),
]

INGREDIENTES = [
    "pollo", "pechuga de pollo", "solomillo de pavo", "filete de ternera", "tacos de ternera",
    "jamon", "lacon", "lacón cocido", "tocino", "chorizo", "morcilla asturiana",
    "filetes de lomo", "lomo", "solomillo de cerdo", "costillas de cerdo", "costillar de cerdo",
    "carne picada", "picadillo", "salchicha", "chistorra", "butifarra", "morcilla de arroz",
    "chuletas de cerdo", "chuletillas de cordero",
    "salmon", "atun suprema", "sardinas", "dorada", "lubina", "bacalao", "gambas", "sepia", "gula",
    "atun en lata", "mejillones", "zamburinas en lata",
    "pasta", "arroz", "fideua", "lentejas", "garbanzos", "fabes", "fabes pintes", "guisantes",
    "tomate", "lechuga", "cebolla", "ajo", "pimiento", "pimiento piquillo", "pimiento de piquillo",
    "zanahoria", "pepinillo", "puerro", "esparragos",
    "patata", "calabacin", "espinacas", "frejoles", "champinones",
    "berenjena", "calabaza", "maiz", "aguacate", "boniato", "setas",
    "huevo", "queso", "mozzarella", "leche", "nata", "curry", "pan rallado", "pan",
    "limon", "aceitunas", "vino blanco", "vino tinto", "sal gorda", "salsa de tomate",
    "tomate frito", "caldo de marisco", "caldo de carne",
    "harina", "levadura",
    "nuggets", "croquetas", "rollitos primavera",
    "manzana", "platano", "naranja", "fresas", "kiwi", "melocoton", "frutos rojos", "uvas",
    "cereales", "tostadas",
]

COLORES_CATEGORIA = {
    "pasta_arroz": "#F9E79F",
    "legumbres": "#A9DFBF",
    "pescado_azul": "#85C1E9",
    "pescado_blanco": "#AED6F1",
    "carne_blanca": "#F5CBA7",
    "carne_roja": "#F1948A",
    "ensalada": "#82E0AA",
    "verdura": "#A3E4D7",
    "desayuno": "#D7BDE2",
    "fritura": "#E59866",
}

DESAYUNOS = [
    "Yogur con cereales y fruta",
    "Yogur con frutos rojos",
    "Tostadas con tomate y jamon",
    "Tostadas con huevo",
    "Tostadas con aguacate",
    "Tostadas con queso fresco y mermelada",
    "Tostadas con mantequilla y miel",
    "Tostadas con tomate y queso",
    "Cereales con leche",
    "Porridge de avena",
]

FRUTAS_TEMPORADA = {
    "invierno": ["naranja", "mandarina", "kiwi", "manzana", "pera", "platano"],
    "primavera": ["fresas", "platano", "manzana", "kiwi", "piña"],
    "verano": ["melocoton", "sandia", "melon", "nectarina", "cerezas", "paraguayo", "albaricoque"],
    "otono": ["uvas", "higos", "granada", "manzana", "pera", "caqui"],
}

FRUTAS = ["manzana", "platano", "naranja", "fresas", "kiwi", "melocoton", "frutos rojos", "uvas"]
