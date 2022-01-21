from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

class SchellingAgent(Agent):
    """
    Schelling Segregasyon Ajanı
    """
    #Sınıfın Başlatılması
    def __init__(self, pos, model, agent_type):
        """
        Yeni bir Schelling Ajanı Yaratılması
        Argümanlar:
           unique_id: Ajana ait eşsiz kimlik bilgisi.
           x, y: Ajanın başlangıçtaki konumu.
           agent_type: Ajanın tipini belirten değişken, tip-1 ya da tip-0. (Azınlık için tip: 1, Çoğunluk için tip: 0)
        """
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type

    #Step üye fonksiyonu
    def step(self):
        similar = 0
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if neighbor.type == self.type:
                similar += 1

        #Eğer ajan mutsuzsa ajanı rastgele boş olan bir konuma taşır
        if similar < self.model.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1


class Schelling(Model):
    """
    Schelling Segregation Model'i için model class'ı
    """
    
    def __init__(self, height=50, width=50, density=0.4, minority_pc=0.2, homophily=3):
        """
        Genişlik ile beraber sistemdeki toplam ajan sayısını tanımlamak için kullanılan gridin dikey ekseni değişkeni
        """
        self.height = height

        """
        Uzunluk ile beraber sistemdeki toplam ajan sayısını tanımlamak için kullanılan gridin yatay ekseni değişkeni
        """
        self.width = width

        """
        Sistemdeki popülasyon yoğunluğunu tanımalamak için kullanılan density(yoğunluk) değişkeni
        [0, 1] aralığında float bir değişken
        """
        self.density = density

        """
        Mavi ve Pembe sayısı arasındaki oran. Mavi azınlık olarak gösterilirken pembe ise çoğunluk olarak gösterilmiştir.
        [0, 1] aralığında float bir değişken.
        Eğer değer 0.5 değerinden yüksekse pembe yerine mavi çoğunluk olarak atfedilir.
        """
        self.minority_pc = minority_pc

        """
        Ajanların mutlu olabilmesi için gerekli olan hemcins komşu sayısını tanımlar.
        ***
        *-*
        ***
        Yukarıda da gösterildiği gibi bir noktanın maksimum 8 komşusu olabilir.
        Minimumda ise bu değer 0'dır.
        Bu nedenle bu değişken [0, 8] aralığında integer değerler alabilir.
        """
        self.homophily = homophily

        """
        Scheduler: Şimdi ise bir scheduler'a ihtiyacıımız var.
        Scheduler hangi ajanların aktive edildiğini kontrol eden özel bir model komponentidir.
        En yaygın scheduler "random activation" modelidir.
        Random Activation, bütün ajanları tek tek rastgele şekilde aktif eder.        
        """
        self.schedule = RandomActivation(self)

        """
        Mesa kütüphanesi altında bulunan space modülü ile Grid'imizi hazırlıyoruz
        """
        self.grid = SingleGrid(width, height, torus=True)

        """
        Data Collection: Simülasyonun her adımından sonra gerekli bilgiyi topladığımızdan emin olmak için data collection olmazsa olmazdır.
        Biz Mesa kütüphanesinden hazır gelen datacollection modülünü kullanacağız.
        Bu sayede tek bilmemiz gereken ajanımızın mutlu olup olmadığı hepsi bu.
        """
        self.happy = 0
        self.datacollector = DataCollector(
            {"happy": "happy"},  # Mutlu ajanların model düzeyinde sayısı.
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]},
        )

        # Ajanları hazırlıyoruz
        """
            Hücrenin koordinatlarının yanı sıra içerdiği veriyi de 
            döndüren bir grid iteratorı kullanıyoruz.(coord_iter)
        """
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if self.random.random() < self.density:
                if self.random.random() < self.minority_pc:
                    agent_type = 1
                else:
                    agent_type = 0

                agent = SchellingAgent((x, y), self, agent_type)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Modeli bir adımlık çalıştır. 
        Eğer tüm ajanlar mutluysa şart sağlanmış demektir.
        Yani adım atmayı bırakabilir kısacası simülasyonu durdurabiliriz.
        """
        self.happy = 0  # Mutlu ajanların sayısını sıfırla
        self.schedule.step()
        # Verileri topla
        self.datacollector.collect(self)
        # Eğer tüm ajanlar mutluysa simülasyonu durdur
        if self.happy == self.schedule.get_agent_count():
            self.running = False