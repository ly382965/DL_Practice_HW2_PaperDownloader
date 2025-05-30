import pygame
import sys
import downloader
import gui

status_message = ""
message_color = gui.COLORS['text']
message_display_start = 0

textbox_scientist = gui.TextBox(150, 50, gui.TEXTBOX_WIDTH, gui.TEXTBOX_HEIGHT, max_length=50)
textbox_year = gui.TextBox(150, 100, gui.TEXTBOX_WIDTH, gui.TEXTBOX_HEIGHT, max_length=4)
textbox_output = gui.TextBox(150, 150, gui.TEXTBOX_WIDTH, gui.TEXTBOX_HEIGHT, max_length=50)

def validate_inputs():
    errors = []
    
    if not textbox_scientist.text.strip():
        errors.append("Scientist name cannot be empty")
        
    try:
        year = int(textbox_year.text)
        if not ((year >= 1970 and year <= 2025) or year == -1):
            errors.append("Year must be between 1970-2025, or -1 for all years")
    except ValueError:
        errors.append("Invalid year format")
        
    output_text = textbox_output.text.strip()
    if output_text and not output_text.endswith(".json"):
        errors.append("File extension must be .json")
        
    return errors

def download_action():
    global status_message, message_color, message_display_start
    
    validation_errors = validate_inputs()
    if validation_errors:
        status_message = "Error: " + " | ".join(validation_errors)
        message_color = gui.COLORS['error']
        message_display_start = pygame.time.get_ticks()
        return

    scientist = textbox_scientist.text.strip()
    year = int(textbox_year.text.strip())
    output_file = textbox_output.text.strip()
    
    if not output_file:
        if year == -1:
            output_file = f"{scientist}_all.json"
        else:
            output_file = f"{scientist}_{year}.json"

    try:
        result = downloader.download_papers(scientist, year, output_file)
        
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
        pygame.draw.rect(gui.screen, gui.COLORS['background'], (50, 270, 500, 30))
        msg_surface = gui.font.render(status_message, True, message_color)
        gui.screen.blit(msg_surface, (50, 270))
        pygame.display.update((50, 270, 500, 30))  
        
        if pygame.time.get_ticks() > message_display_start + 10000:
            status_message = ""
            pygame.display.update((50, 270, 500, 30))  

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    delta_time = clock.tick(60) / 1000  # Increase to 60 FPS
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        textbox_scientist.handle_event(event)
        textbox_year.handle_event(event)
        textbox_output.handle_event(event)
        download_button.handle_event(event)

    textbox_scientist.update(delta_time)
    textbox_year.update(delta_time)
    textbox_output.update(delta_time)

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