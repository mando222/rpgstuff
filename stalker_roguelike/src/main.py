import pygame
import sys
from .game.game_state import GameState
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE

# Initialize Pygame
pygame.init()

def main():
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    # Create game state
    game = GameState()
    
    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Pass other events to game state
            game.handle_input(event)
        
        # Update game state
        game.update()
        
        # Render
        game.render(screen)
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(FPS)

if __name__ == "__main__":
    main()
