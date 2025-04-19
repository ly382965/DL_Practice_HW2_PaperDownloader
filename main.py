"""
Paper Downloader GUI Application
Integrated with download_papers API and input validation
"""

import pygame
import sys
import downloader

# Initialize Pygame
pygame.init()

# Constants
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

# Global states
status_message = ""
message_color = COLORS['text']
message_display_start = 0

# UI Components
textbox_scientist = TextBox(150, 50, TEXTBOX_WIDTH, TEXTBOX_HEIGHT, max_length=50)
textbox_year = TextBox(150, 100, TEXTBOX_WIDTH, TEXTBOX_HEIGHT, max_length=4)
textbox_output = TextBox(150, 150, TEXTBOX_WIDTH, TEXTBOX_HEIGHT, max_length=50)

def validate_inputs():
    """Input validation logic"""
    errors = []
    
    if not textbox_scientist.text.strip():
        errors.append("Scientist name cannot be empty")
        
    try:
        year = int(textbox_year.text)
        if year < 1900 or year > 2100:
            errors.append("Year must be between 1900-2100")
    except ValueError:
        errors.append("Invalid year format")
        
    if not textbox_output.text.strip():
        errors.append("Output filename required")
    elif not textbox_output.text.endswith(".csv"):
        errors.append("File extension must be .csv")
        
    return errors

def download_action():
    """Download button handler"""
    global status_message, message_color, message_display_start
    
    # Validate inputs
    validation_errors = validate_inputs()
    if validation_errors:
        status_message = "Error: " + " | ".join(validation_errors)
        message_color = COLORS['error']
        message_display_start = pygame.time.get_ticks()
        return

    # Get parameters
    scientist = textbox_scientist.text.strip()
    year = int(textbox_year.text.strip())
    output_file = textbox_output.text.strip()

    try:
        # Call download API
        result = downloader.download_papers(scientist, year, output_file)
        
        # Handle result
        if result.get("success"):
            status_message = f"Downloaded {result['count']} papers to {output_file}"
            message_color = COLORS['success']
        else:
            status_message = f"Download failed: {result.get('error', 'Unknown error')}"
            message_color = COLORS['error']
            
        message_display_start = pygame.time.get_ticks()
    except Exception as e:
        status_message = f"System error: {str(e)}"
        message_color = COLORS['error']
        message_display_start = pygame.time.get_ticks()

download_button = Button(250, 200, 100, 40, "Download", download_action)

def draw_labels():
    """Draw static labels"""
    labels = [
        ("Name:", (50, 55)),
        ("Year:", (50, 105)),
        ("Output File:", (50, 155))
    ]
    for text, pos in labels:
        text_surface = font.render(text, True, COLORS['text'])
        screen.blit(text_surface, pos)

def draw_message():
    """Display status messages with partial updates"""
    global status_message
    if status_message:
        # 清除旧消息区域
        pygame.draw.rect(screen, COLORS['background'], (50, 270, 500, 30))
        # 绘制新消息
        msg_surface = font.render(status_message, True, message_color)
        screen.blit(msg_surface, (50, 270))
        pygame.display.update((50, 270, 500, 30))  # 局部更新
        
        # Auto-clear after 10 seconds
        if pygame.time.get_ticks() > message_display_start + 10000:
            status_message = ""
            pygame.display.update((50, 270, 500, 30))  # 清除区域更新

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    delta_time = clock.tick(60) / 1000  # 提升至60 FPS
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 组件事件分发
        textbox_scientist.handle_event(event)
        textbox_year.handle_event(event)
        textbox_output.handle_event(event)
        download_button.handle_event(event)

    # 组件状态更新
    textbox_scientist.update(delta_time)
    textbox_year.update(delta_time)
    textbox_output.update(delta_time)

    # 高效渲染
    screen.fill(COLORS['background'])
    draw_labels()
    textbox_scientist.draw(screen)
    textbox_year.draw(screen)
    textbox_output.draw(screen)
    download_button.draw(screen)
    draw_message()
    
    pygame.display.flip()

pygame.quit()
sys.exit()