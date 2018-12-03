from Mic import*
from Scene import*


class game (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.freq = 0.0

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
        Treble = pygame.image.load('Treble.png')
        Treble.convert()
        pygame.display.set_caption("Intonation Hero")
        pygame.display.set_icon(Treble)
        pygame.mouse.set_visible(True)
        timer = pygame.time.Clock()
        running = True

        manager = SceneMananger()

        while running:
            timer.tick(40)

            if pygame.event.get(QUIT):
                running = False
                thread2.running = False
                return
                
            self.freq = thread2.freq
            manager.scene.handle_events(pygame.event.get())
            manager.scene.update(self.freq)
            manager.scene.render(screen)
            pygame.display.flip()



if __name__ == "__main__":

    # Create new threads
    thread1 = game()
    thread2 = mic()

    

    # Start new Threads 
    thread1.start()
    thread2.start()
   
