import pygame
import sys
import random

LEBAR_LAYAR = 1200
TINGGI_LAYAR = 650
FPS = 60

GRAVITASI = 0.7
KECEPATAN_JALAN = 7
KECEPATAN_LOMPAT = -18

pygame.init()

layar = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
pygame.display.set_caption("Dungeon Boss Battle")

clock = pygame.time.Clock()

def load_gambar(file, ukuran):
    try:
        img = pygame.image.load(file).convert_alpha()
        return pygame.transform.scale(img, ukuran)
    except:
        dummy = pygame.Surface(ukuran)
        dummy.fill((120,120,120))
        return dummy

img_player = load_gambar("Heroo.png", (90,70))
img_tanah = load_gambar("pasir.png", (80,50))
img_bg = load_gambar("Desert.png", (LEBAR_LAYAR,TINGGI_LAYAR))
img_monster1 = load_gambar("monster1.png", (60,60))
img_monster2 = load_gambar("monster2.png", (70,70))
img_boss = load_gambar("boss.png", (120,120))
img_heart = load_gambar("heart.png", (40,40))
img_pedang = load_gambar("pedang.png", (40,40))
img_tombak = load_gambar("tombak.png", (40,40))
img_busur = load_gambar("busur.png", (40,40))
img_slash = load_gambar("slash.png",(120,80))
img_arrow = load_gambar("arrow.png",(50,20))
img_spear_attack = load_gambar("spear_attack.png",(160,60))

panah_list = []
tombak_fx_timer = 0

class Monster:
    def __init__(self, x, y, hp, damage, kecepatan, image, boss=False):
        self.rect = pygame.Rect(x, y, 120 if boss else 70, 120 if boss else 70)
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.kecepatan = kecepatan
        self.image = image
        self.alive = True
        self.boss = boss
        self.attack_timer = 0
        self.sedang_memukul = False

class Item:
    def __init__(self, x, y, tipe):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.tipe = tipe

daftar_tanah = []
daftar_monster = []
daftar_item = []

def buat_platform(x_awal, panjang, y_pos=550):
    for i in range(panjang):
        daftar_tanah.append(pygame.Rect(x_awal + i*60, y_pos, 60, 50))

# ================= GENERATE MAP & PLATFORM =================
buat_platform(0, 10)       
buat_platform(1000, 12)    
buat_platform(2150, 12)    
buat_platform(3300, 12)    
buat_platform(4450, 15)    

posisi_tanah_atas = [
    (400, 380), (600, 260), (1200, 380), (1500, 260), 
    (2300, 350), (2600, 240), (3500, 350), (3800, 240)
]
for x, y in posisi_tanah_atas:
    buat_platform(x, 1, y)

# ================= PENEMPATAN MONSTER & STATS =================
monster1 = Monster(1400, 480, 50, 10, 3, img_monster1)
monster2 = Monster(3500, 480, 80, 15, 4, img_monster2)
boss = Monster(5100, 430, 250, 20, 2, img_boss, True)
daftar_monster.append(monster1)
daftar_monster.append(monster2)
daftar_monster.append(boss)

# ================= PENEMPATAN ITEM =================
weapon1 = random.choice(["pedang", "tombak", "busur"])
weapon2 = random.choice(["pedang", "tombak", "busur"])

daftar_item.append(Item(420, 330, weapon1))  
daftar_item.append(Item(620, 210, weapon2))  

daftar_item.append(Item(1220, 330, "heart"))
daftar_item.append(Item(1520, 210, "heart"))
daftar_item.append(Item(2620, 190, "heart"))
daftar_item.append(Item(3820, 190, "heart"))

# ================= PLAYER & STATE GAME =================
player = pygame.Rect(100, 400, 50, 70)
vel_y = 0
on_ground = False
max_lompatan = 2
jumlah_lompatan = 2
player_hp = 150
max_hp = 150
damage_player = 10
senjata_aktif = "Tangan"
kamera_x = 0
status_kalah = False
status_menang = False
sedang_menyerang = False
attack_timer = 0
arah_player = 1

def gambar_hp_bar(x, y, hp, max_hp):
    if max_hp > 0:
        pygame.draw.rect(layar, (255,0,0), (x, y, 60, 8))
        pygame.draw.rect(layar, (0,255,0), (x, y, int(60 * (hp / max_hp)), 8))

# Main Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN and not status_kalah and not status_menang:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if jumlah_lompatan < max_lompatan:
                    vel_y = KECEPATAN_LOMPAT
                    jumlah_lompatan += 1
                    on_ground = False

            if event.key == pygame.K_f:
                if not sedang_menyerang:
                    if senjata_aktif == "Busur":
                        panah_list.append({"x": player.centerx, "y": player.centery, "arah": arah_player})
                        sedang_menyerang = True
                        attack_timer = 15
                    elif senjata_aktif == "Tombak":
                        tombak_fx_timer = 15
                        sedang_menyerang = True
                        attack_timer = 15
                    else:
                        sedang_menyerang = True
                        attack_timer = 12

    if not status_kalah and not status_menang:
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -KECEPATAN_JALAN
            arah_player = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = KECEPATAN_JALAN
            arah_player = 1
            
        player.x += dx
        for tanah in daftar_tanah:
            if player.colliderect(tanah):
                if dx > 0:
                    player.right = tanah.left
                elif dx < 0:
                    player.left = tanah.right
                    
        vel_y += GRAVITASI
        player.y += vel_y
        on_ground = False
        
        for tanah in daftar_tanah:
            if player.colliderect(tanah):
                if vel_y > 0:
                    player.bottom = tanah.top
                    vel_y = 0
                    on_ground = True
                    jumlah_lompatan = 0
                elif vel_y < 0:
                    player.top = tanah.bottom
                    vel_y = 0
                    
        if player.y > TINGGI_LAYAR:
            status_kalah = True

        kamera_x += (player.x - kamera_x - LEBAR_LAYAR // 3) / 12

        if sedang_menyerang and senjata_aktif != "Busur":
            jangkauan = 160 if senjata_aktif == "Tombak" else 90
            if arah_player == 1:
                attack_rect = pygame.Rect(player.right, player.y, jangkauan, 60)
            else:
                attack_rect = pygame.Rect(player.left - jangkauan, player.y, jangkauan, 60)

            if attack_timer == 10:  
                for monster in daftar_monster:
                    if monster.alive and attack_rect.colliderect(monster.rect):
                        monster.hp -= damage_player
                        if monster.hp <= 0:
                            monster.hp = 0
                            monster.alive = False

        if sedang_menyerang:
            attack_timer -= 1
            if attack_timer <= 0:
                sedang_menyerang = False

        for arrow in panah_list[:]:
            arrow["x"] += 15 * arrow["arah"]
            arrow_rect = pygame.Rect(arrow["x"], arrow["y"], 50, 20)
            
            hit_monster = False
            for monster in daftar_monster:
                if monster.alive and monster.rect.colliderect(arrow_rect):
                    monster.hp -= damage_player
                    if monster.hp <= 0:
                        monster.hp = 0
                        monster.alive = False
                    hit_monster = True
                    break
                    
            if hit_monster or abs(arrow["x"] - player.x) > 1200:
                if arrow in panah_list:
                    panah_list.remove(arrow)

        for monster in daftar_monster:
            if not monster.alive:
                continue
                
            jarak = abs(monster.rect.centerx - player.centerx)
            monster.sedang_memukul = False
            
            if jarak < 500:
                if monster.rect.centerx < player.centerx:
                    monster.rect.x += monster.kecepatan
                elif monster.rect.centerx > player.centerx:
                    monster.rect.x -= monster.kecepatan
                    
                if jarak < 80:
                    monster.sedang_memukul = True
                    monster.attack_timer += 1
                    if monster.attack_timer > 30:  
                        player_hp -= monster.damage
                        monster.attack_timer = 0
                else:
                    monster.attack_timer = 0
            else:
                monster.attack_timer = 0

        for item in daftar_item[:]:
            if player.colliderect(item.rect):
                if item.tipe == "heart":
                    player_hp += 25
                    if player_hp > max_hp:
                        player_hp = max_hp
                elif item.tipe == "pedang":
                    damage_player = 15
                    senjata_aktif = "Pedang"
                elif item.tipe == "tombak":
                    damage_player = 20
                    senjata_aktif = "Tombak"
                elif item.tipe == "busur":
                    damage_player = 12
                    senjata_aktif = "Busur"
                daftar_item.remove(item)

        if player_hp <= 0:
            player_hp = 0
            status_kalah = True

        if not boss.alive:
            status_menang = True

        if boss.alive and boss.hp <= boss.max_hp // 2:
            boss.damage = 35
            boss.kecepatan = 4  

    # ================= DRAWING SECTION =================
    layar.blit(img_bg, (0, 0))

    for tanah in daftar_tanah:
        if abs(tanah.x - kamera_x) < LEBAR_LAYAR + 200:
            layar.blit(img_tanah, (tanah.x - kamera_x, tanah.y))

    for item in daftar_item:
        gambar = img_heart
        if item.tipe == "pedang":
            gambar = img_pedang
        elif item.tipe == "tombak":
            gambar = img_tombak
        elif item.tipe == "busur":
            gambar = img_busur
        layar.blit(gambar, (item.rect.x - kamera_x, item.rect.y))

    for monster in daftar_monster:
        if not monster.alive:
            continue
        layar.blit(monster.image, (monster.rect.x - kamera_x, monster.rect.y))
        gambar_hp_bar(monster.rect.x - kamera_x + (monster.rect.width//2 - 30), monster.rect.y - 15, monster.hp, monster.max_hp)
        
        if monster.sedang_memukul:
            pygame.draw.rect(layar, (255, 0, 0), (monster.rect.x - kamera_x, monster.rect.y - 5, monster.rect.width, 5))

    layar.blit(img_player, (player.centerx - 40 - kamera_x, player.y))

    if sedang_menyerang and senjata_aktif == "Pedang":
        if arah_player == 1:
            layar.blit(img_slash, (player.right - int(kamera_x) - 10, player.y))
        else:
            layar.blit(pygame.transform.flip(img_slash, True, False), (player.left - int(kamera_x) - 110, player.y))

    if tombak_fx_timer > 0:
        if arah_player == 1:
            layar.blit(img_spear_attack, (player.right - int(kamera_x), player.y + 5))
        else:
            layar.blit(pygame.transform.flip(img_spear_attack, True, False), (player.left - int(kamera_x) - 160, player.y + 5))
        tombak_fx_timer -= 1

    for arrow in panah_list:
        if arrow["arah"] == 1:
            layar.blit(img_arrow, (arrow["x"] - int(kamera_x), arrow["y"] - 10))
        else:
            layar.blit(pygame.transform.flip(img_arrow, True, False), (arrow["x"] - int(kamera_x) - 50, arrow["y"] - 10))

    font_ui = pygame.font.SysFont("Arial", 28, True)
    font_besar = pygame.font.SysFont("Impact", 100)

    pygame.draw.rect(layar, (100,0,0), (20, 20, 250, 25))
    pygame.draw.rect(layar, (0,255,0), (20, 20, int(250 * (player_hp / max_hp)), 25))
    
    teks_hp = font_ui.render(f"HP : {int(player_hp)}", True, (255,255,255))
    layar.blit(teks_hp, (25, 50))
    
    teks_weapon = font_ui.render(f"Weapon : {senjata_aktif}", True, (255,255,0))
    layar.blit(teks_weapon, (25, 85))
    
    teks_damage = font_ui.render(f"Damage : {damage_player}", True, (255,200,50))
    layar.blit(teks_damage, (25, 120))

    progress = min(max(player.x / 5200, 0), 1)
    pygame.draw.rect(layar, (80,80,80), (350, 20, 300, 20))
    pygame.draw.rect(layar, (0,200,255), (350, 20, int(300 * progress), 20))
    teks_progress = font_ui.render("Dungeon Progress", True, (255,255,255))
    layar.blit(teks_progress, (410, 45))

    if status_kalah:
        overlay = pygame.Surface((LEBAR_LAYAR, TINGGI_LAYAR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        layar.blit(overlay, (0, 0))
        teks = font_besar.render("GAME OVER", True, (255,50,50))
        rect = teks.get_rect(center=(LEBAR_LAYAR//2, TINGGI_LAYAR//2))
        layar.blit(teks, rect)
        sub = font_ui.render("Boss gagal dikalahkan!", True, (255,255,255))
        layar.blit(sub, (LEBAR_LAYAR//2 - 110, TINGGI_LAYAR//2 + 80))
        
    if status_menang:
        overlay = pygame.Surface((LEBAR_LAYAR, TINGGI_LAYAR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        layar.blit(overlay, (0, 0))
        teks = font_besar.render("YOU WIN", True, (50,255,50))
        rect = teks.get_rect(center=(LEBAR_LAYAR//2, TINGGI_LAYAR//2))
        layar.blit(teks, rect)
        sub = font_ui.render("Boss Defeated! Game Selesai.", True, (255,255,255))
        layar.blit(sub, (LEBAR_LAYAR//2 - 140, TINGGI_LAYAR//2 + 80))

    pygame.display.flip()
    clock.tick(FPS)

# Menutup aplikasi secara bersih saat loop selesai
pygame.quit()
sys.exit()