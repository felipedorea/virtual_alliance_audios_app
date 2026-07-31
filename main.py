import os
import sys
import asyncio
import ctypes
import pygame
import mutagen
import flet as ft


def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return os.path.join(base, relative_path)


def get_documents():
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
    return buf.value


AUDIO_DIR = os.path.join(get_documents(), "Virtual Alliance Boarding Audios", "audios")
os.makedirs(AUDIO_DIR, exist_ok=True)

TAB_STAGES  = ["Boas-Vindas Partida", "Decolagem", "Cruzeiro", "Serv. Bordo", "Descida", "Pouso", "Desembarque", "Boas-Vindas Chegada"]
TAB_FOLDERS = ["0. Boas-Vindas Partida", "1. Decolagem", "2. Cruzeiro", "3. Serv. Bordo", "4. Descida", "5. Pouso", "6. Desembarque", "7. Boas-Vindas Chegada"]
TAB_OLD     = ["boas-vindas-partida", "decolagem", "cruzeiro", "serv. bordo", "descida", "pouso", "desembarque", "boas-vindas-chegada"]

for i, folder in enumerate(TAB_FOLDERS):
    old = os.path.join(AUDIO_DIR, TAB_OLD[i])
    new = os.path.join(AUDIO_DIR, folder)
    if os.path.isdir(old) and not os.path.isdir(new):
        os.rename(old, new)
    os.makedirs(new, exist_ok=True)

BG_PAGE        = "#0D1B2A"
BG_HEADER      = "#111827"
BG_CARD        = "#1A2740"
BG_CARD_ACTIVE = "#0F2E26"
BG_PLAYER      = "#111827"
ACCENT         = "#00F5C4"
TEXT_PRIMARY   = "#F0F4F8"
TEXT_SECONDARY = "#8899AA"
BORDER_ACTIVE  = "#00F5C4"
BORDER_CARD    = "#1E3050"
SLIDER_TRACK   = "#1E3050"

VERSION = "1.0.0"
DISCORD_URL = "https://discord.gg/kjKfRmSEBr"


def scan_audio_files(subdir):
    path = os.path.join(AUDIO_DIR, subdir)
    if not os.path.isdir(path):
        return []
    valid = (".mp3", ".wav", ".ogg", ".m4a", ".flac")
    return sorted(f for f in os.listdir(path) if f.lower().endswith(valid))


def display_name(filename):
    return filename.rsplit(".", 1)[0]


def main(page: ft.Page):
    page.title = "Audios de cabine Virtual Alliance"
    page.bgcolor = BG_PAGE
    page.window.width = 400
    page.window.height = 710
    page.window.resizable = False
    page.window.maximizable = False
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK

    pygame.mixer.init()
    page.on_close = lambda e: (pygame.mixer.quit(), pygame.quit())

    def format_time(secs):
        m = int(secs // 60)
        s = int(secs % 60)
        return f"{m}:{s:02d}"

    current_tab = 0
    current_folder = TAB_FOLDERS[0]
    files = scan_audio_files(current_folder)

    durations = {}
    for f in files:
        try:
            af = mutagen.File(os.path.join(AUDIO_DIR, current_folder, f))
            durations[f] = af.info.length if af and af.info.length else 0
        except Exception:
            durations[f] = 0

    current_index = -1

    tocando_label = ft.Text(
        "REPRODUZINDO",
        color=TEXT_SECONDARY,
        size=9,
        weight=ft.FontWeight.BOLD,
    )
    tocando_text = ft.Text(
        "Nenhum audio selecionado",
        color=TEXT_SECONDARY,
        size=13,
        weight=ft.FontWeight.W_600,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )
    progress_bar = ft.Slider(
        min=0, max=1, value=0,
        active_color=ACCENT,
        inactive_color=SLIDER_TRACK,
        thumb_color=ACCENT,
        height=14,
    )
    time_start = ft.Text("0:00", color=TEXT_SECONDARY, size=9)
    time_end   = ft.Text("0:00", color=TEXT_SECONDARY, size=9)

    volume_slider = ft.Slider(
        min=0, max=100, value=80, divisions=20,
        active_color=ACCENT,
        inactive_color=SLIDER_TRACK,
        thumb_color=ACCENT,
        height=10,
        expand=True,
    )
    volume_label = ft.Text("80%", color=TEXT_SECONDARY, size=9, width=24)

    pause_btn = ft.IconButton(
        icon=ft.Icons.STOP_ROUNDED,
        icon_color=BG_PAGE,
        icon_size=18,
        bgcolor=ACCENT,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            padding=6,
        ),
    )

    playlist_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    card_refs    = []
    tab_containers = []
    search_query = ""

    def update_ui():
        if 0 <= current_index < len(files):
            tocando_text.value = display_name(files[current_index])
            tocando_text.color = TEXT_PRIMARY
            tocando_label.color = ACCENT
            dur = durations.get(files[current_index], 0)
            time_end.value = format_time(dur)
            if not pygame.mixer.music.get_busy():
                progress_bar.value = 0
                time_start.value = "0:00"
        else:
            progress_bar.value = 0
            time_start.value = "0:00"
            time_end.value = "0:00"
            tocando_text.value = "Nenhum audio selecionado"
            tocando_text.color = TEXT_SECONDARY
            tocando_label.color = TEXT_SECONDARY

        for i, (card, btn) in enumerate(card_refs):
            if i == current_index:
                card.bgcolor = BG_CARD_ACTIVE
                card.border = ft.Border.all(1, BORDER_ACTIVE)
            else:
                card.bgcolor = BG_CARD
                card.border = ft.Border.all(1, BORDER_CARD)

        for i, tab in enumerate(tab_containers):
            tab.content.color = ACCENT if i == current_tab else TEXT_SECONDARY
            tab.content.weight = ft.FontWeight.W_600 if i == current_tab else ft.FontWeight.W_400
            tab.border = ft.Border(
                left=ft.BorderSide(0.5, "#1E3050"),
                right=ft.BorderSide(0.5, "#1E3050"),
                top=ft.BorderSide(0.5, "#1E3050"),
                bottom=ft.BorderSide(2, ACCENT if i == current_tab else "#1E3050"),
            )

        page.update()

    monitor_gen = 0

    def start_monitor():
        nonlocal monitor_gen
        monitor_gen += 1
        my_gen = monitor_gen

        async def monitor():
            while monitor_gen == my_gen:
                await asyncio.sleep(0.5)
                if monitor_gen != my_gen:
                    break
                if pygame.mixer.music.get_busy():
                    pos = pygame.mixer.music.get_pos() / 1000.0
                    dur = durations.get(files[current_index], 0)
                    progress_bar.value = min(pos / dur, 1.0) if dur > 0 else 0
                    time_start.value = format_time(pos)
                    page.update()
                else:
                    progress_bar.value = 0
                    time_start.value = "0:00"
                    page.update()
                    break

        page.run_task(monitor)

    def stop_monitor():
        nonlocal monitor_gen
        monitor_gen += 1

    def play_idx(idx):
        nonlocal current_index
        stop_monitor()
        current_index = idx
        path = os.path.join(AUDIO_DIR, current_folder, files[idx])
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            tocando_text.value = f"Erro: {e}"
            tocando_text.color = "#EF5350"
            page.update()
            return
        update_ui()
        start_monitor()

    def play_click(idx):
        stop_monitor()
        if pygame.mixer.music.get_busy() and current_index == idx:
            pygame.mixer.music.stop()
        play_idx(idx)

    def stop_audio(e):
        nonlocal current_index
        stop_monitor()
        pygame.mixer.music.stop()
        current_index = -1
        update_ui()

    pause_btn.on_click = stop_audio

    def update_volume_label(e):
        pygame.mixer.music.set_volume(e.control.value / 100)
        volume_label.value = f"{int(e.control.value)}%"
        page.update()

    volume_slider.on_change = update_volume_label

    def build_card(i, fname):
        play_btn = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            icon_color=ACCENT,
            icon_size=16,
            bgcolor="transparent",
            style=ft.ButtonStyle(
                shape=ft.CircleBorder(),
                side=ft.BorderSide(1, ACCENT),
                padding=2,
            ),
            on_click=lambda _, idx=i: play_click(idx),
        )
        name_text = ft.Text(
            display_name(fname),
            color=TEXT_PRIMARY,
            size=13,
            weight=ft.FontWeight.W_500,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        row = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color=ACCENT, size=18),
                    bgcolor="#00F5C418",
                    border_radius=8,
                    padding=8,
                ),
                ft.Column(
                    [name_text],
                    spacing=1,
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                play_btn,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )
        card = ft.Container(
            content=row,
            bgcolor=BG_CARD,
            border=ft.Border.all(1, BORDER_CARD),
            border_radius=12,
            padding=ft.Padding(left=12, right=12, top=3, bottom=3),
            on_click=lambda _, idx=i: play_click(idx),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                    )
        return card, play_btn

    for i, fname in enumerate(files):
        card, btn = build_card(i, fname)
        card_refs.append((card, btn))
        playlist_col.controls.append(card)

    def on_search_change(e):
        nonlocal search_query
        search_query = e.control.value.strip().lower()
        apply_search_filter()

    def apply_search_filter():
        visible_count = 0
        for i, (card, btn) in enumerate(card_refs):
            fname = display_name(files[i]).lower()
            match = not search_query or search_query in fname
            card.visible = match
            if match:
                visible_count += 1
        playlist_count.value = f"{visible_count} de {len(files)} faixas" if search_query else f"{len(files)} faixas"
        update_ui()

    search_field = ft.TextField(
        hint_text="Pesquisar...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=8,
        border_color=BORDER_CARD,
        focused_border_color=ACCENT,
        filled=True,
        fill_color=BG_CARD,
        color=TEXT_PRIMARY,
        hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=11),
        text_size=12,
        height=32,
        content_padding=ft.Padding(left=8, right=8, top=0, bottom=0),
        on_change=on_search_change,
        dense=True,
        expand=True,
    )

    playlist_count = ft.Text(f"{len(files)} faixas", color=TEXT_SECONDARY, size=11)

    def rebuild_playlist():
        nonlocal files, durations, current_index, card_refs, search_query
        search_query = ""
        search_field.value = ""
        stop_monitor()
        files = scan_audio_files(current_folder)
        durations.clear()
        for f in files:
            try:
                af = mutagen.File(os.path.join(AUDIO_DIR, current_folder, f))
                durations[f] = af.info.length if af and af.info.length else 0
            except Exception:
                durations[f] = 0
        if current_index >= 0 and current_index >= len(files):
            current_index = -1
        elif current_index < 0:
            pass
        card_refs.clear()
        playlist_col.controls.clear()
        for i, fname in enumerate(files):
            card, btn = build_card(i, fname)
            card_refs.append((card, btn))
            playlist_col.controls.append(card)
        playlist_count.value = f"{len(files)} faixas"
        playlist_count.update()
        update_ui()

    def on_tab_click(tab_index):
        nonlocal current_tab, current_folder, current_index
        if tab_index == current_tab:
            return
        stop_monitor()
        pygame.mixer.music.stop()
        current_tab = tab_index
        current_folder = TAB_FOLDERS[current_tab]
        current_index = -1
        rebuild_playlist()

    def build_tab(label, index, top_padding=6, bottom_padding=6):
        return ft.Container(
            content=ft.Text(
                label, color=ACCENT if index == current_tab else TEXT_SECONDARY, size=12,
                weight=ft.FontWeight.W_600 if index == current_tab else ft.FontWeight.W_400,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor="transparent",
            border=ft.Border(
                left=ft.BorderSide(0.5, "#1E3050"),
                right=ft.BorderSide(0.5, "#1E3050"),
                top=ft.BorderSide(0.5, "#1E3050"),
                bottom=ft.BorderSide(2, ACCENT if index == current_tab else "#1E3050"),
            ),
            border_radius=0,
            padding=ft.Padding(left=0, right=0, top=top_padding, bottom=bottom_padding),
            expand=True,
            on_click=lambda _, idx=index: on_tab_click(idx),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

    tab0 = build_tab(TAB_STAGES[0], 0, top_padding=12, bottom_padding=12)
    row1_tabs = ft.Row(
        [build_tab(TAB_STAGES[i], i) for i in range(1, 4)],
        spacing=0,
    )
    row2_tabs = ft.Row(
        [build_tab(TAB_STAGES[i], i) for i in range(4, 7)],
        spacing=0,
    )
    tab7 = build_tab(TAB_STAGES[7], 7, top_padding=12, bottom_padding=12)

    tab_grid = ft.Container(
        content=ft.Column([
            ft.Row([tab0], spacing=0),
            row1_tabs,
            row2_tabs,
            ft.Row([tab7], spacing=0),
        ], spacing=0),
        padding=ft.Padding(left=16, right=16, top=2, bottom=0),
    )

    tab_containers.append(tab0)
    for t in row1_tabs.controls:
        tab_containers.append(t)
    for t in row2_tabs.controls:
        tab_containers.append(t)
    tab_containers.append(tab7)

    def build_step(num, title, desc):
        return ft.Column(
            [
                ft.Text(f"PASSO {num}", color=ACCENT, size=9, weight=ft.FontWeight.BOLD),
                ft.Text(title, color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_600),
                ft.Text(desc, color=TEXT_SECONDARY, size=12),
            ],
            spacing=3,
        )

    tutorial_title = ft.Text(
        "Como usar",
        color=TEXT_PRIMARY,
        size=17,
        weight=ft.FontWeight.BOLD,
    )

    tutorial_content = ft.Column(
        [
            build_step(1, "Escolha a etapa do voo",
                       "Clique na aba do estágio desejado (Boas-Vindas Partida, "
                       "Decolagem, Cruzeiro, Serv. Bordo, Descida, Pouso, "
                       "Desembarque ou Boas-Vindas Chegada). A lista carrega os "
                       "áudios dessa etapa."),
            build_step(2, "Pesquise uma faixa",
                       "Use o campo de busca para filtrar rapidamente os áudios "
                       "pelo nome."),
            build_step(3, "Reproduza",
                       "Toque em uma faixa ou no botão de play para começar a "
                       "reprodução."),
            build_step(4, "Controle o áudio",
                       "Ajuste o volume no controle deslizante e acompanhe o "
                       "progresso da faixa. Use o botão de parar para encerrar."),
            build_step(5, "Atualize a lista",
                       "Depois de adicionar novos arquivos, clique no botão de "
                       "atualizar para recarregar a lista."),
            build_step(6, "Onde ficam os áudios",
                       "Coloque os arquivos em Documentos > Virtual Alliance "
                       "Boarding Audios > audios, nas pastas por etapa "
                       "(0. Boas-Vindas Partida, 1. Decolagem etc.)."),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def open_tutorial(e):
        asyncio.create_task(page.push_route("/tutorial"))

    def close_tutorial(e):
        asyncio.create_task(page.push_route("/"))

    header = ft.Container(
        content=ft.Stack(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Image(
                                    src=resource_path("logo.png"),
                                    height=90,
                                ),
                                ft.Container(expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.FOLDER_ROUNDED,
                                    icon_color=TEXT_SECONDARY,
                                    icon_size=18,
                                    tooltip="Abrir pasta de audios",
                                    on_click=lambda e: os.startfile(AUDIO_DIR),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.MENU_BOOK_ROUNDED,
                                    icon_color=TEXT_SECONDARY,
                                    icon_size=18,
                                    tooltip="Tutorial",
                                    on_click=open_tutorial,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH_ROUNDED,
                                    icon_color=TEXT_SECONDARY,
                                    icon_size=18,
                                    tooltip="Atualizar lista",
                                    on_click=lambda e: rebuild_playlist(),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        tab_grid,
                    ],
                    spacing=2,
                ),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    spans=[
                                        ft.TextSpan(
                                            "Visite nosso site",
                                            url="https://virtualalliance-gilt.vercel.app/",
                                            style=ft.TextStyle(color=ACCENT, size=11),
                                        )
                                    ],
                                ),
                                ft.Text("•", color=TEXT_SECONDARY, size=11),
                                ft.Text(
                                    spans=[
                                        ft.TextSpan(
                                            "Entre no Discord",
                                            url=DISCORD_URL or None,
                                            style=ft.TextStyle(color=ACCENT, size=11),
                                        )
                                    ],
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        ft.Text(
                            VERSION,
                            color=TEXT_SECONDARY,
                            size=11,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    top=0,
                    left=0,
                    right=0,
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ]
        ),
        bgcolor=BG_HEADER,
        padding=ft.Padding(left=16, right=8, top=6, bottom=14),
    )

    playlist_header = ft.Container(
        content=playlist_count,
        padding=ft.Padding(left=16, right=0, top=8, bottom=4),
    )

    search_container = ft.Container(
        content=search_field,
        padding=ft.Padding(left=12, right=12, top=4, bottom=4),
    )

    player_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [tocando_label, tocando_text],
                            spacing=0,
                            expand=True,
                        ),
                        pause_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                progress_bar,
                ft.Row(
                    [time_start, ft.Container(expand=True), time_end],
                    spacing=0,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.VOLUME_UP_ROUNDED, color=TEXT_SECONDARY, size=12),
                        volume_slider,
                        volume_label,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
            ],
            spacing=2,
        ),
        bgcolor=BG_PLAYER,
        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
    )

    main_col = ft.Column(
        [
            header,
            playlist_header,
            search_container,
            ft.Container(
                content=playlist_col,
                expand=True,
                padding=ft.Padding(left=12, right=12, top=4, bottom=4),
            ),
            player_panel,
        ],
        spacing=0,
        expand=True,
    )

    main_view = ft.View(
        route="/",
        bgcolor=BG_PAGE,
        padding=0,
        controls=[main_col],
    )

    tutorial_view = ft.View(
        route="/tutorial",
        bgcolor=BG_PAGE,
        padding=0,
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                                    icon_color=TEXT_PRIMARY,
                                    icon_size=20,
                                    tooltip="Voltar",
                                    on_click=close_tutorial,
                                ),
                                tutorial_title,
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(color=BORDER_CARD, height=1),
                        tutorial_content,
                    ],
                    spacing=10,
                ),
                bgcolor=BG_HEADER,
                padding=ft.Padding(left=12, right=16, top=10, bottom=16),
                expand=True,
            ),
        ],
    )

    def route_change(e):
        page.views.clear()
        page.views.append(main_view)
        if page.route == "/tutorial":
            page.views.append(tutorial_view)
        page.update()

    page.on_route_change = route_change
    page.views.clear()
    page.views.append(main_view)
    page.update()
    update_ui()


if __name__ == "__main__":
    ft.run(main)
