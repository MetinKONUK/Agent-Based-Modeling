from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from Model import Schelling #Model.py dosyasından Schelling sınıfını import edelim

#Programın bu kısmı görselleştirme amacına hizmet etmektedir
"""
Mesanın bize sunduğu visualization modülünü kullanarak web tarayıcısı üzerinde ajanları
konumlarında renk ayrımlarını yaparak göstermemizi sağlar
Ayrıca simüle etmeyi kolaylaştırır ve çeşitli kullanışlı ayarlara sahiptir.
Lokal bilgisayarımızı üzerinde bir localhost oluşturur.
"""
class HappyElement(TextElement):
    #Yapıcı fonksiyonumuz
    def __init__(self):
        pass

    """
    Kaç tane mutlu ajanımız olduğunu belirten bir yazı döndürür.
    """
    def render(self, model):
        return "Happy agents: " + str(model.happy)


def schelling_draw(agent):
    if agent is None:
        return
    """
    Tuvalimiz için portrayal metodumuz
    """
    """
    Ilk olarak başlangıç portrayalimizi oluşturuyoruz
    Portrayal web sunucumuza şekilleri nasıl çizmesi gerektiğini belirten bir sözlüktür.
    Pythondaki dictionary yapısı JSON dosya formatına çok benzediğinden 
    JSON objesine kolaylıkla dönüştürülecektir
    """
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}

    """
    Ajanın tipine göre iç ve dış renklerini belirliyoruz.
    Bu programda Mavi ve Pembe ajanımız olacak.
    """
    if agent.type == 0:
        portrayal["Color"] = ["#031163", "#1fbfb8"] #Çeper rengi, İç renk, Mavi Ajanımız
        portrayal["stroke_color"] = "#00FF00"
    else:
        portrayal["Color"] = ["#ed3572", "#da68a0"] #Çeper rengi, İç renk, Pembe Ajanımız
        portrayal["stroke_color"] = "#000000"
    return portrayal #Portrayal objemizi döndürüyoruz


happy_element = HappyElement()

#Tuvalimizi ve grafiğimizi hazırlıyoruz.
canvas_element = CanvasGrid(schelling_draw, 50, 50, 500, 500)
happy_chart = ChartModule([{"Label": "happy", "Color": "#000080"}])

#Modelimizi konfigüre ediyoruz.
model_params = {
    "height": 50,
    "width": 50,
    "density": UserSettableParameter("slider", "Agent density", 0.4, 0.1, 1.0, 0.1),
    "minority_pc": UserSettableParameter(
        "slider", "Fraction minority", 0.2, 0.00, 1.0, 0.05
    ),
    "homophily": UserSettableParameter("slider", "Homophily", 3, 0, 8, 1),
}

"""
Ve son olarak yukarıda tanımladığımız konfigürasyonlarla sunucumuzu başlatıyoruz.
"""
server = ModularServer(
    Schelling, [canvas_element, happy_element, happy_chart], "Schelling", model_params)

