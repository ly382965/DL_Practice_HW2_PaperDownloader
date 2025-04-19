import pygame
import sys
import downloader
import gui

# Global states
status_message = ""
message_color = gui.COLORS['text']
message_display_start = 0

# UI Components
textbox_scientist = gui.TextBox(150, 50, gui.TEXTBOX_WIDTH, gui.TEXTBOX_HEIGHT, max_length=50)
textbox_year = gui.TextBox(150, 100, gui.TEXTBOX_WIDTH, gui.TEXTBOX_HEIGHT, max_length=4)
textbox_output = gui.TextBox(150, 150, gui.TEXTBOX_WIDTH, gui.TEXTBOX_HEIGHT, max_length=50)

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
    elif not textbox_output.text.endswith(".json"):
        errors.append("File extension must be .json")
        
    return errors

def download_action():
    """Download button handler"""
    global status_message, message_color, message_display_start
    
    # Validate inputs
    validation_errors = validate_inputs()
    if validation_errors:
        status_message = "Error: " + " | ".join(validation_errors)
        message_color = gui.COLORS['error']
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
            message_color = gui.COLORS['success']
        else:
            status_message = f"Download failed: {result.get('error', 'Unknown error')}"
            message_color = gui.COLORS['error']
            
        message_display_start = pygame.time.get_ticks()
    except Exception as e:
        status_message = f"System error: {str(e)}"
        message_color = gui.COLORS['error']
        message_display_start = pygame.time.get_ticks()

download_button = gui.Button(250, 200, 100, 40, "Download", download_action)

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
    gui.screen.fill(gui.COLORS['background'])
    draw_labels()
    textbox_scientist.draw(gui.screen)
    textbox_year.draw(gui.screen)
    textbox_output.draw(gui.screen)
    download_button.draw(gui.screen)
    draw_message()
    
    pygame.display.flip()

pygame.quit()
sys.exit()