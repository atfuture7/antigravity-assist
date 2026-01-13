# Implementation Plan - Edit Area & Move Tool

## Proposed Changes

### HTML Refactor (`index.html`)
- **Edit Area**: Create a new container `<div class="edit-area">` above the `.component-area`.
- **Buttons**: Move `Reset`, `Delete`, `Save`, `Load` into this new area. Add `Move` button.
- **Carousel**: Structure the Edit Area with `<button id="edit-left">`, `div.edit-grid`, `<button id="edit-right">`.

### CSS Updates (`style.css`)
- **Layout**: Adjust flex ratios. Maybe `Drawing (5)`, `Edit (1)`, `Component (1)`, `Input (1)`.
- **Edit Styling**: Style similar to Component Area but distinct (different background?).
- **Element Interaction**: Styles for elements being moved (e.g., `cursor: grabbing`).

### Logic Updates (`script.js`)
- **Edit Carousel**:
    - `editButtons` array (objects or just dom elements).
    - `editStartIndex`, `editPageSize` (e.g., 3 buttons visible).
    - Handlers for `edit-left` and `edit-right`.
- **Move Tool**:
    - `toolState.moveMode`.
    - toggle logic (disable other buttons).
    - `mousedown` on `.canvas-element`: `startMove(el)`.
    - `mousemove`: `updateMove`.
    - `mouseup`: `stopMove`.
- **Interaction Conflicts**: Ensure Move Mode, Delete Mode, and Drawing tools don't conflict (mutually exclusive).

## Verification Plan
1. **Layout**: Verify 4 sections.
2. **Edit Carousel**: Check if buttons scroll (Save, Load, Reset, Delete, Move = 5 items. If size=3 or 4, scrolling works).
3. **Move Tool**:
    - Turn on Move.
    - Drag element. Verify it moves.
    - Drag background (panning). Verify panning still works or is disabled? "Pressing this button will make all other buttons interactive [sic/inactive]".
    - Usually "Move" implies moving elements, Panning moves view. They can coexist if targets differ (element vs bg).
    - Verify other interactions disabled.
