import pygame, random

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.playlist = []          # danh sách nhạc nền
        self.played = set()         # theo dõi bài nào đã mở
        self.current = None
        self.paused_pos = 0
        self.is_bg = True
        self.default_volume = 0.4
        self.MUSIC_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_END)

        self.temp_playlist = []
        self.temp_played = set()
        self.temp_volume = 0.6

    def set_playlist(self, tracks, volume=0.4):
        self.playlist = tracks[:]
        self.played.clear()
        self.default_volume = volume

    def _next_song(self):
        if not self.playlist:
            return None
        available = [t for t in self.playlist if t not in self.played]
        if not available:
            self.played.clear()
            available = self.playlist[:]
        song = random.choice(available)
        self.played.add(song)
        return song

    def play_next(self):
        song = self._next_song()
        if song:
            pygame.mixer.music.load(song)
            pygame.mixer.music.set_volume(self.default_volume)
            pygame.mixer.music.play()
            self.current = song
            self.paused_pos = 0
            self.is_bg = True

    def update(self, events):
        for e in events:
            if e.type == self.MUSIC_END:
                if self.is_bg:
                    self.play_next()
                else:
                    self._play_temp_next()

    def play_temp(self, path, volume=0.6):
        """Phát nhạc thắng/thua, tạm dừng nhạc nền"""
        if self.is_bg and self.current:
            self.paused_pos = pygame.mixer.music.get_pos() / 1000
            pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()
        self.is_bg = False

    def resume_bg(self):
        if self.current:
            # Phát lại từ vị trí paused
            pygame.mixer.music.load(self.current)
            pygame.mixer.music.set_volume(self.default_volume)
            pygame.mixer.music.play(0, self.paused_pos)
            self.is_bg = True
            self.paused_pos = 0

    def play_temp_playlist(self, tracks, volume=0.6):
        """Phát danh sách nhạc thắng/thua, tạm dừng nhạc nền"""
        if self.is_bg and self.current:
            self.paused_pos = pygame.mixer.music.get_pos() / 1000
            pygame.mixer.music.stop()
        self.temp_playlist = tracks[:]
        self.temp_played = set()
        self.temp_volume = volume
        self._play_temp_next()
        self.is_bg = False

    def _play_temp_next(self):
        if not self.temp_playlist:
            self.resume_bg()
            return

        available = [t for t in self.temp_playlist if t not in self.temp_played]
        if not available:
            # Temp playlist hết → quay lại nhạc nền
            self.resume_bg()
            return

        song = random.choice(available)
        self.temp_played.add(song)
        pygame.mixer.music.load(song)
        pygame.mixer.music.set_volume(self.temp_volume)
        pygame.mixer.music.play()
