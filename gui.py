import pygame

# 初始化
pygame.init()
SCREEN_SIZE = (600, 450)
COLORS = {
    'background': (255, 255, 255),
    'text': (0, 0, 0),
    'active_border': (173, 216, 230),
    'inactive_border': (200, 200, 200),
    'button': (200, 200, 200),
    'error': (255, 0, 0),
    'success': (0, 128, 0)
}
FONT_SIZE = 24
TEXTBOX_WIDTH = 300
TEXTBOX_HEIGHT = 30

# Initialize display
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Paper Downloader")
try:
    font = pygame.font.Font(None, FONT_SIZE)  # Use system default font
except:
    font = pygame.font.SysFont("arial", FONT_SIZE)

class TextBox:
    """Interactive text input box component"""
    
    def __init__(self, x, y, width, height, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.active = False
        self.max_length = max_length
        self.cursor_visible = True
        self.cursor_timer = 0
        self.last_render = None  # 缓存渲染结果

    def handle_event(self, event):
        """Handle input events with partial updates"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if was_active != self.active:
                pygame.display.update(self.rect)
            
        if self.active and event.type == pygame.KEYDOWN:
            # 处理删除键
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            # 处理普通输入
            elif event.unicode.isprintable() and len(self.text) < self.max_length:
                self.text += event.unicode
            
            # 局部更新优化
            self.last_render = font.render(self.text, True, COLORS['text'])
            pygame.display.update(self.rect)

    def update(self, dt):
        """Optimized cursor animation"""
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer > 0.4:  # 加快光标闪烁速度
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
                pygame.display.update(self.rect)  # 仅更新光标区域

    def draw(self, surface):
        """Efficient rendering with caching"""
        # 绘制边框
        border_color = COLORS['active_border'] if self.active else COLORS['inactive_border']
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # 使用缓存渲染
        if self.last_render is None:
            self.last_render = font.render(self.text, True, COLORS['text'])
        surface.blit(self.last_render, (self.rect.x + 5, self.rect.y + 5))
        
        # 绘制光标
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + self.last_render.get_width()
            pygame.draw.line(surface, COLORS['text'], 
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.y + self.rect.h - 5))

class Button:
    """Clickable button component"""
    
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
                
    def draw(self, surface):
        pygame.draw.rect(surface, COLORS['button'], self.rect)
        text_surface = font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

def draw_labels():
    """Draw static labels"""
    labels = [
        ("Name:", (50, 55)),
        ("Year:", (50, 105)),
        ("Output File:", (50, 155))
    ]
    for text, pos in labels:
        text_surface = gui.font.render(text, True, gui.COLORS['text'])
        gui.screen.blit(text_surface, pos)

def draw_message():
    """Display status messages with partial updates"""
    global status_message
    if status_message:
        # 清除旧消息区域
        pygame.draw.rect(gui.screen, gui.COLORS['background'], (50, 270, 500, 30))
        # 绘制新消息
        msg_surface = gui.font.render(status_message, True, message_color)
        gui.screen.blit(msg_surface, (50, 270))
        pygame.display.update((50, 270, 500, 30))  # 局部更新
        
        # Auto-clear after 10 seconds
        if pygame.time.get_ticks() > message_display_start + 10000:
            status_message = ""
            pygame.display.update((50, 270, 500, 30))  # 清除区域更新