
import rec_lib
import thinkdsp 
from Entities import*
import Mic
import Utils
import Constants


DISPLAY = (Constants.WIN_WIDTH, Constants.WIN_HEIGHT)
DEPTH = 0
FLAGS = 0



class Scene(object):
    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError



class GameScene(Scene):
    def __init__(self, chapterno, sectionno, exerciseno):
        super(GameScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)
        self.font2 = pygame.font.SysFont('timesnewroman', 36)
        self.entities = pygame.sprite.Group()
        self.player = PlayerArrow(Constants.WIN_WIDTH/18.5, Constants.WIN_HEIGHT/2.15)
        self.player.scene = self  ########### ERROR #############
        self.platforms = []
        self.playerscore = 0
        self.chapterno = chapterno
        self.sectionno = sectionno
        self.exerciseno = exerciseno
        self.hiscore = Utils.get_hiscore(self)
        self.tup = rec_lib.rep_or_dep("IE_"+str(self.chapterno)+'.'+str(self.sectionno), self.exerciseno)
        self.call = self.tup[0]
        self.response = self.tup[1]
        self.calldata = thinkdsp.read_wave(self.call)
        self.responsedata = thinkdsp.read_wave(self.response)
        self.pause = False
        self.start = True
        self.end = False
        self.duration = self.responsedata.duration
        self.callsound = pygame.mixer.Sound(self.call)
        self.repsound = pygame.mixer.Sound(self.response)
        #self.recf0 = Mic.f0value(self.responsedata) #Calc
        self.recf0 = rec_lib.get_speaker("IE_"+str(self.chapterno), self.sectionno) #Speaker reclib
        self.transcription = rec_lib.trans("IE_"+str(self.chapterno)+'.'+str(self.sectionno), self.exerciseno)
        self.hirender = False
        self.ps = 0
        self.freq = 1

        plst = Mic.pitchpoints(self.responsedata, self.recf0)

        # build the level
        x = 200
        prey = (0, 0)
        for p in plst:

            if p>0:
                #y = Mic.notepos(Mic.note_no_oct(p))
                self.ps += 1
                y = -Mic.f0dev(p, self.recf0)+Constants.HALF_HEIGHT
                point = Platform(x, y)
                self.platforms.append(point)
                self.entities.add(point)
                prey = (x, y)  
            
            x += 20
        nx = prey[0]
        ny = prey[1]
        exitblock = ExitBlock(nx, ny)
        self.platforms.append(exitblock)
        self.entities.add(exitblock)

        transcription = Transcription(Constants.WIN_WIDTH*.5, Constants.WIN_HEIGHT*.8, self.transcription)
        self.entities.add(transcription)

        self.entities.add(self.player)


    def render(self, screen):

        screen.fill(Constants.grey)

        #Title
        s = 'Chapitre ' + str(self.chapterno) + '.' +str(self.sectionno)
        text = self.font.render(s, True, (Constants.black))
        screen.blit(text, (Constants.HALF_WIDTH/6, 0+Constants.WIN_HEIGHT*.1))

        #PlayerScore
        s = 'Score: ' + str(self.playerscore)
        text = self.font.render(s, True, (Constants.black))
        screen.blit(text, (Constants.WIN_WIDTH/2, 0+Constants.WIN_HEIGHT*.1))

        #HiScore
        s = 'Hiscore: ' + str(self.hiscore)
        text = self.font.render(s, True, (Constants.black))
        screen.blit(text, (Constants.WIN_WIDTH/2, 0+Constants.WIN_HEIGHT*.025))

     
        #Bar Scale
        nh = (Constants.WIN_HEIGHT/10)
        bary = (Constants.WIN_HEIGHT/2)
        pygame.draw.line(screen, Constants.black, (0, bary + nh*2), (Constants.WIN_WIDTH, bary + nh*2), 1)
        pygame.draw.line(screen, Constants.black, (0, bary + nh), (Constants.WIN_WIDTH, bary + nh), 1)
        pygame.draw.line(screen, Constants.black, (0, bary), (Constants.WIN_WIDTH, bary), 1)
        pygame.draw.line(screen, Constants.black, (0, bary - nh), (Constants.WIN_WIDTH, bary - nh), 1)
        pygame.draw.line(screen, Constants.black, (0, bary - nh*2), (Constants.WIN_WIDTH, bary - nh*2), 1)

        #Arrow Bars
        nx = (Constants.WIN_WIDTH/11)
        barx = (Constants.WIN_WIDTH*0.05)
        pygame.draw.line(screen, Constants.blue, (barx, bary - nh*2), (barx, bary + nh*2), 2)
        pygame.draw.line(screen, Constants.blue, (barx + nx, bary + nh*2), (barx + nx, bary - nh*2), 2)

        #Repeat button
        s = '>'
        text = self.font2.render(s, True, (Constants.black))
        playbutton(screen, self, 1, text, Constants.WIN_WIDTH/16, Constants.WIN_HEIGHT-Constants.WIN_HEIGHT/16, 35, 35, Constants.blue_light, Constants.green, self.repsound)
        
        if self.hirender:
            pygame.draw.rect(screen, Constants.white,(200,200,400,200))
            text = self.font2.render('Nouveau Hiscore!', True, (Constants.black))
            screen.blit(text, (275, 200))
            percent = str(int((self.playerscore/(self.ps*5))*100))+" %"
            text = self.font.render(percent, True, (Constants.black))
            screen.blit(text, (350, 275))
            text = self.font2.render('> Appuyez sur Espace pour continuer <', True, (Constants.black))
            screen.blit(text, (150, 500))

        for e in self.entities:
            if isinstance(e, PlayerArrow) and self.freq > 0:
                screen.blit(e.image, (e.rect.x, e.rect.y))
            elif isinstance(e, Transcription):
                screen.blit(e.text, (e.rect.x, e.rect.y))
            else:
                screen.blit(e.image, (e.rect.x, e.rect.y))


    def update(self, freq):
        #self.player.update(freq, self.platforms, Constants.HALF_HEIGHT) #, TOP, BOTTOM)
        self.freq = freq
        if self.pause:
            for e in self.entities:
                self.entities.update(freq, self.platforms, Constants.HALF_HEIGHT, Constants.HALF_WIDTH)
                if isinstance(e, Transcription):
                    
                     if e.rect.right <= 0:
                        self.entities.remove(e)
                else:
                    if e.rect.left <= 0:
                        if isinstance(e, ExitBlock):
                            self.end = True
                            if self.playerscore > self.hiscore:
                                Utils.WriteScore(self, self.playerscore)
                                self.hirender = True

                        self.entities.remove(e)
                        self.platforms.remove(e)


    def exit(self):
        if rec_lib.repdep("IE_"+str(self.chapterno)+'.'+str(self.sectionno)) == 0:
            if self.exerciseno < len(rec_lib.ex_enum("IE_"+str(self.chapterno)+'.'+str(self.sectionno))):
                self.manager.go_to(GameScene(self.chapterno, self.sectionno, self.exerciseno+1))
            else:
                self.manager.go_to(SectionScene("Section Complète!", "> Appuyez sur Espace pour continuer à la section suivante <", self.chapterno, self.sectionno, self.exerciseno))

        elif rec_lib.repdep("IE_"+str(self.chapterno)+'.'+str(self.sectionno)) == 1:
            if self.exerciseno < len(rec_lib.ex_enum("IE_"+str(self.chapterno)+'.'+str(self.sectionno)))/2:
                self.manager.go_to(GameScene(self.chapterno, self.sectionno, self.exerciseno+1))
            else:
                self.manager.go_to(SectionScene("Section Complète!", "> Appuyez sur Espace pour continuer à la section suivante <", self.chapterno, self.sectionno, self.exerciseno))

    def handle_events(self, events):

        if self.start:
            pygame.mixer.Sound.play(self.callsound)
            self.start = False     

        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                self.manager.go_to(TitleScene())
            if e.type == KEYDOWN and e.key == K_SPACE:
                self.pause = not self.pause

            if self.end:
                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    self.manager.go_to(TitleScene())
                if e.type == KEYDOWN and e.key == K_SPACE:
                    self.exit()

    def score(self):
        self.playerscore += 5






class FinalScene(object):

    def __init__(self, text):
        self.text = text
        super(FinalScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)

    def render(self, screen):
        screen.fill(Constants.grey)
        text1 = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text1, (250, 50))

    def update(self, freq):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key != K_SPACE:
                self.manager.go_to(TitleScene())
            elif e.type == KEYDOWN and e.key == K_SPACE:
                self.manager.go_to(TitleScene())







class ChapterScene(object):

    def __init__(self, text, text2, chapno):
        self.text = text
        self.text2 = text2
        self.chapno = chapno
        super(ChapterScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)
        self.font2 = pygame.font.SysFont('timesnewroman', 28)

    def render(self, screen):
        screen.fill(Constants.grey)
        text1 = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text1, (Constants.WIN_WIDTH/4, Constants.WIN_HEIGHT/12))
        text2 = self.font2.render(self.text2, True, (0, 0, 0))
        screen.blit(text2, (75, 500))

    def update(self, freq):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key != K_SPACE:
                self.manager.go_to(TitleScene())
            elif e.type == KEYDOWN and e.key == K_SPACE:
                if self.chapno+1 <= 20:
                    self.manager.go_to(GameScene(self.chapno+1, 1, 1))
                else:
                    self.manager.go_to(FinalScene("Jeu Complet!"))







class SectionScene(object):

    def __init__(self, text, text2, chapno, sectno, exno):
        self.text = text
        self.text2 = text2
        self.chapno = chapno
        self.sectno = sectno
        self.exno = exno
        super(SectionScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)
        self.font2 = pygame.font.SysFont('timesnewroman', 28)

    def render(self, screen):
        screen.fill(Constants.grey)
        text1 = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text1, (Constants.WIN_WIDTH/4, Constants.WIN_HEIGHT/12))
        text2 = self.font2.render(self.text2, True, (0, 0, 0))
        screen.blit(text2, (75, 500))

    def update(self, freq):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key != K_SPACE:
                self.manager.go_to(TitleScene())
            elif e.type == KEYDOWN and e.key == K_SPACE:
                if self.sectno+1 <= len(rec_lib.sect_enum("IE_"+str(self.chapno))):
                    self.manager.go_to(IntroScene(self.chapno, self.sectno+1))
                else:
                    self.manager.go_to(ChapterScene("Chapitre Complet!", "> Appuyez sur Espace pour continuer au chapitre suivant <", self.chapno))
                






class IntroScene(object):

    def __init__(self, chapno, sectno):
        super(IntroScene, self).__init__()
        self.start = True
        self.chapterselected = chapno
        self.sectionselected = sectno
        self.response = rec_lib.rep_or_dep("IE_"+str(self.chapterselected)+'.'+str(self.sectionselected), 1)[1]
        self.calldata = rec_lib.Intro("IE_" + str(self.chapterselected)+"."+str(self.sectionselected))
        self.callsound = pygame.mixer.Sound(self.calldata)
        self.responsedata = thinkdsp.read_wave(self.response)
        self.transcription = rec_lib.trans("IE_"+str(self.chapterselected)+'.'+str(self.sectionselected), 1)
        self.font = pygame.font.SysFont('timesnewroman', 36)
        self.text = self.font.render(self.transcription, True, (Constants.black))
        #self.recf0 = Mic.f0value(self.responsedata) #Calc
        self.recf0 = rec_lib.get_speaker("IE_"+str(self.chapterselected), self.sectionselected) #Speaker reclib
        self.platforms = []

        plst = Mic.pitchpoints(self.responsedata, self.recf0)
        print(self.transcription)
        # build the level
        x = 200
        for p in plst:
            if p>0:
                #y = Mic.notepos(Mic.note_no_oct(p))
                y = -Mic.f0dev(p, self.recf0)+Constants.HALF_HEIGHT
                point = Platform(x, y)
                self.platforms.append(point)          
            x += 20

    def render(self, screen):
        screen.fill(Constants.grey)
        screen.blit(self.text, (250, 100))
        for e in self.platforms:
            screen.blit(e.image, (e.rect.x, e.rect.y))

    def update(self, freq):
        pass

    def handle_events(self, events):
        if self.start:
            pygame.mixer.Sound.play(self.callsound)
            self.start = False
        for e in events:
            if e.type == KEYDOWN and e.key != K_SPACE:
                pygame.mixer.stop()
                self.manager.go_to(TitleScene())
            elif e.type == KEYDOWN and e.key == K_SPACE:
                pygame.mixer.stop()
                self.manager.go_to(GameScene(self.chapterselected, self.sectionselected, 1))






class TitleScene(object):

    def __init__(self):
        super(TitleScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)
        self.sfont = pygame.font.SysFont('timesnewroman', 32)
        self.ssfont = pygame.font.SysFont('timesnewroman', 22)
        self.chapterselected = 0
        self.sectionselected = 0
        self.exerciseselected = 0
        self.setselect = False
        self.hiselect = False
        self.f0 = Constants.SPEAKER


    def render(self, screen):
        #Background
        screen.fill((Constants.grey))

        #Title
        text1 = self.font.render('Intonation Hero', True, (Constants.black))
        screen.blit(text1, (250, 50))

        #F0 TESTING
        text2 = self.sfont.render(str(self.f0), True, (Constants.black))
        screen.blit(text2, (725, 50))

        tt= self.font.render('*', True, (Constants.black))
        #Settings
        button(screen, self, 1, tt, 50, 50, 35, 35, Constants.blue_light, Constants.green, Utils.setselect)

        t = self.sfont.render(' %', True, (Constants.black))
        #Hi_Scores
        button(screen, self, 1, t, 50, 100, 35, 35, Constants.red, Constants.green, Utils.hiselect)

        t = self.sfont.render('>', True, (Constants.black))
        #Hi_Scores
        button(screen, self, 1, t, 750, 100, 25, 25, Constants.blue_light, Constants.green, Utils.upselect)

        t = self.sfont.render('<', True, (Constants.black))
        #Hi_Scores
        button(screen, self, 1, t, 725, 100, 25, 25, Constants.blue_light, Constants.green, Utils.downselect)

        #Chapter
        t = self.sfont.render('Chapitre', True, (Constants.black))
        screen.blit(t, (350, 150))
        n = 1
        p = 1
        for x in rec_lib.chap_enum():
            text = self.sfont.render(str(n), True, (Constants.black))
            y = Constants.HALF_HEIGHT - 75
            x = 100+50*n
            if n > 10:
                y = Constants.HALF_HEIGHT-25
                x = 100+50*p
                p +=1

            button(screen, self, n, text, x, y, 35, 35, Constants.grey, Constants.green, Utils.chapset)
            n+=1

        #Section
        if self.chapterselected != 0:
            text2 = self.sfont.render('Section', True, (Constants.black))
            screen.blit(text2, (350, Constants.HALF_HEIGHT+25))
            n = 1
            for r in rec_lib.sect_enum("IE_" + str(self.chapterselected)):
                text = self.sfont.render(str(n), True, (Constants.black))
                y = Constants.HALF_HEIGHT+75
                x = 100+50*n

                button(screen, self, n, text, x, y, 35, 35, Constants.grey, Constants.green, Utils.secset)
                n+=1

        #Exercise
        if self.sectionselected != 0:
            text3 = self.sfont.render('Exercice', True, (Constants.black))
            screen.blit(text3, (350, Constants.HALF_HEIGHT+125))
            n = 1
            if rec_lib.repdep("IE_" + str(self.chapterselected)+"."+str(self.sectionselected)) == 0:
                i = 0
                for r in rec_lib.ex_enum("IE_" + str(self.chapterselected)+"."+str(self.sectionselected)):
                    i += 1
                    text = self.sfont.render("", True, (Constants.black))
                    y = Constants.HALF_HEIGHT+175
                    x = 100+50*n

                    if Utils.get_hi(int(self.chapterselected), int(self.sectionselected), i) > 0:
                        color = Constants.green
                    else:
                        color = Constants.blue_light

                    button(screen, self, n, text, x, y, 35, 35, color, Constants.black, Utils.exset)
                    n+=1
            if rec_lib.repdep("IE_" + str(self.chapterselected)+"."+str(self.sectionselected)) == 1:
                i = 0
                for r in range(round(len(rec_lib.ex_enum("IE_" + str(self.chapterselected)+"."+str(self.sectionselected)))/2)):
                    i += 1
                    text = self.sfont.render("", True, (Constants.black))
                    y = Constants.HALF_HEIGHT+175
                    x = 100+50*n

                    if Utils.get_hi(int(self.chapterselected), int(self.sectionselected), i) > 0:
                        color = Constants.green
                    else:
                        color = Constants.blue_light

                    button(screen, self, n, text, x, y, 35, 35, color, Constants.black, Utils.exset)
                    n+=1

        #Game Start
        if self.exerciseselected != 0:
            text4 = self.sfont.render('> Appuyez sur Espace pour Commencer <', True, (Constants.black))
        
            screen.blit(text4, (Constants.HALF_WIDTH/3 , Constants.WIN_HEIGHT-Constants.WIN_HEIGHT/12))

    def update(self, freq):
        pass

    def handle_events(self, events):
        for e in events:
            if self.setselect == True:
                self.manager.go_to(SettingScene())
            if self.hiselect == True:
                self.manager.go_to(HighScene())
            if e.type == KEYDOWN and e.key == K_SPACE and self.exerciseselected == 1 and self.sectionselected != 0:
                #pygame.mouse.set_visible(False)
                self.manager.go_to(IntroScene(self.chapterselected, self.sectionselected))
            if e.type == KEYDOWN and e.key == K_SPACE and self.exerciseselected > 1 and self.sectionselected != 0:
                #pygame.mouse.set_visible(False)
                self.manager.go_to(GameScene(self.chapterselected, self.sectionselected, self.exerciseselected))






class OpenScene(object):

    def __init__(self):
        self.text = "Intonation Hero"
        self.text2 = "Bonjour, je m'appelle ____"
        self.text3 = "enregistrez"
        self.text4 = " "
        super(OpenScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)
        self.font2 = pygame.font.SysFont('timesnewroman', 36)
        self.speaker = Constants.SPEAKER
        self.image = pygame.image.load('Treble.png')
        self.freq = 0
        self.record = False
        self.f0array = []

    def render(self, screen):
        if self.speaker > 0:
            screen.fill(Constants.grey)
            text1 = self.font.render(self.text, True, (0, 0, 0))
            screen.blit(text1, (250, 75))
            #moving trebels and quarters
            # e = 0
            # x = 0
            # y = 0
            # for i in range(round(Constants.WIN_HEIGHT/20)):
            #     y += Constants.WIN_HEIGHT/20
            #     for i in range(round(Constants.WIN_WIDTH/20)):
            #         x += Constants.WIN_WIDTH/20
            #         if e == 0:
            #             e += 1
            #             image = pygame.image.load('Treble.png')
            #         else:
            #             e -= 1
            #             image = pygame.image.load('Arrow.png')
            #         image.convert()
            #         rect = Rect(x, y, Constants.WIN_HEIGHT/20, Constants.WIN_WIDTH/20)
            #         screen.blit(image, (rect.x, rect.y))
            rect = Rect(275, 300, Constants.WIN_HEIGHT/1, Constants.WIN_WIDTH/20)
            screen.blit(self.image, (rect.x, rect.y))

        else:
            screen.fill(Constants.grey)
            text1 = self.font.render(self.text, True, (0, 0, 0))
            screen.blit(text1, (250, 75))
            text2 = self.font2.render(self.text2, True, (0, 0, 0))
            screen.blit(text2, (250, 300))
            text3 = self.font2.render(self.text3, True, (0, 0, 0))
            button(screen, self, 1, text3, 250, 400, 350, 35, Constants.red, Constants.green, Utils.recordselect)

            if self.record:
                i = 0
                while i < 20000:
                    text4 = self.font2.render(self.text4, True, (0, 0, 0))
                    button(screen, self, 1, text4, 250, 400, 350, 35, Constants.green, Constants.green, Utils.nullselect)
                    i += 1
                    self.f0array.append(self.freq)
                newspeaker = int(Mic.f0v(self.f0array))
                rec_lib.write_settings(Constants.SPEED, newspeaker)
                Constants.SPEAKER = newspeaker
                self.speaker = newspeaker


        
        #else:
            #self.manager.go_to(NewScene())

    def update(self, freq):
        self.freq = freq

    def handle_events(self, events):
        for e in events:
            if self.speaker > 0:
                if e.type == KEYDOWN and e.key != K_SPACE:
                    self.manager.go_to(TitleScene())
                elif e.type == KEYDOWN and e.key == K_SPACE:
                    self.manager.go_to(TitleScene())






class SettingScene(object):

    def __init__(self):
        self.text1 = "Settings"
        self.text2 = "<"
        self.text3 = "Game Speed"
        self.text4 = "Difficulty"
        self.text5 = "New Game"
        self.text6 = ""
        self.text7 = "Are You Sure?" 
        self.text8 = "(This will delete all your saved games)"
        super(SettingScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)
        self.font2 = pygame.font.SysFont('timesnewroman', 36)
        self.menuselect = False
        self.newselect = False
        self.gamespeed = Constants.SPEED
        self.difficulty = 0
        self.newgame = False

    def render(self, screen):
        screen.fill(Constants.grey)
        text1 = self.font.render(self.text1, True, (0, 0, 0))
        text2 = self.font2.render(self.text2, True, (0, 0, 0))
        text3 = self.font2.render(self.text3, True, (0, 0, 0))
        text4 = self.font2.render(self.text4, True, (0, 0, 0))
        text5 = self.font2.render(self.text5, True, (0, 0, 0))
        text6 = self.font2.render(self.text6, True, (0, 0, 0))
        text7 = self.font2.render(self.text7, True, (0, 0, 0))
        text8 = self.font2.render(self.text8, True, (0, 0, 0))

        #Title
        screen.blit(text1, (300, 50))

        #Speed
        screen.blit(text3, (300, 200))
        b = Constants.WIN_WIDTH/4 + 25
        n = 6
        for x in range(6-self.gamespeed):
            n -= 1
            b += 50 
            speedbutton(screen, self, n, text6, b, 275, 50, 50, Constants.green, Constants.red, Utils.speedselect)

        for x in range(self.gamespeed-1):
            n -= 1
            b += 50 
            speedbutton(screen, self, n, text6, b, 275, 50, 50, Constants.red, Constants.green, Utils.speedselect)


        #New Game
        button(screen, self, 1, text5, 285, 350, 225, 75, Constants.red, Constants.blue, Utils.newselect)

        #Are You Sure?
        if self.newselect == True:
            button(screen, self, 1, text7, 285, 450, 225, 75, Constants.red, Constants.red, Utils.newgame)
            screen.blit(text8, (150,525))

        #Menu
        button(screen, self, 1, text2, 50, 50, 35, 35, Constants.blue_light, Constants.green, Utils.menuselect)

    def update(self, freq):
        pass

    def handle_events(self, events):
        for e in events:
            if self.newgame == True:
                self.manager.go_to(OpenScene())
            if self.menuselect == True:
                self.manager.go_to(TitleScene())
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                self.manager.go_to(TitleScene())
            elif e.type == KEYDOWN and e.key == K_SPACE:
                self.manager.go_to(TitleScene())






class HighScene(object):

    def __init__(self):
        self.text1 = "Hi Scores"
        self.text2 = "<"
        super(HighScene, self).__init__()
        self.font = pygame.font.SysFont('timesnewroman', 56)
        self.font2 = pygame.font.SysFont('timesnewroman', 36)
        self.sfont = pygame.font.SysFont('timesnewroman', 32)
        self.menuselect = False
        self.chapterselected = 0
        self.sectionselected = 0

    def render(self, screen):
        screen.fill(Constants.grey)
        text1 = self.font.render(self.text1, True, (0, 0, 0))
        text2 = self.font2.render(self.text2, True, (0, 0, 0))
        screen.blit(text1, (250, 50))

        #Menu
        button(screen, self, 1, text2, 50, 50, 35, 35, Constants.blue_light, Constants.green, Utils.menuselect)

        #Chapter
        n = 1
        p = 1
        for x in rec_lib.chap_enum():
            text = self.sfont.render(str(n), True, (Constants.black))
            y = 50+50*n
            x = Constants.WIN_WIDTH/10
            if n > 10:
                y = 50+50*p
                x += x
                p +=1

            button(screen, self, n, text, x, y, 35, 35, Constants.grey, Constants.green, Utils.chapset)
            n+=1

        #Section
        if self.chapterselected != 0:
            #text2 = self.sfont.render('Section', True, (Constants.black))
            #screen.blit(text2, (350, Constants.HALF_HEIGHT+25))
            n = 1
            for r in rec_lib.sect_enum("IE_" + str(self.chapterselected)):
                text = self.sfont.render(str(n), True, (Constants.black))
                y = 100+50*n
                x = Constants.WIN_WIDTH/10*3

                button(screen, self, n, text, x, y, 35, 35, Constants.grey, Constants.green, Utils.secset)
                n+=1

        #Score
        if self.sectionselected != 0:
            
            file = open("savefile.txt", "r")
        
            n = self.sectionselected
            for x in range(self.chapterselected-1):
                secs = rec_lib.sect_enum("IE_" + str(x+1))
                for z in secs:
                    n += 1

            nu = 0
            lst = []
            for l in range(n):
                lst = file.readline()

            
            last = 1
            first = lst.find(",")
            p = 0

            while first != -1:
                score = lst[last:first]
                text = self.sfont.render(str(p+1)+"    "+str(score), True, (Constants.black))
                p+=1
                y = 100+50*nu
                x = Constants.WIN_WIDTH*.75
                screen.blit(text, (x, y))
                last = first+2
                first = lst.find(",", first+1)
                nu+=1

            y = 100+50*nu
            text = self.sfont.render(str(p+1)+"    "+str(lst[last:len(lst)-2]), True, (Constants.black))
            screen.blit(text, (x, y))
            file.close()

    def update(self, freq):
        pass

    def handle_events(self, events):
        for e in events:
            if self.menuselect == True:
                self.manager.go_to(TitleScene())
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                self.manager.go_to(TitleScene())
            elif e.type == KEYDOWN and e.key == K_SPACE:
                self.manager.go_to(TitleScene())






class SceneMananger(object):
    def __init__(self):
        self.go_to(OpenScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self