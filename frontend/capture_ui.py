from playwright.sync_api import sync_playwright
import time
import os

os.makedirs('d:/repo/screenshots', exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    
    routes = ['/', '/students', '/courses', '/exams', '/analysis', '/warnings']
    
    for route in routes:
        print(f"Navigating to {route}")
        page.goto(f'http://localhost:5173{route}')
        page.wait_for_load_state('networkidle')
        # Wait a bit for Entrance animations
        time.sleep(1)
        name = route.replace('/', '') if route != '/' else 'home'
        page.screenshot(path=f'd:/repo/screenshots/{name}.png', full_page=True)
        print(f"Saved {name}.png")

    browser.close()
