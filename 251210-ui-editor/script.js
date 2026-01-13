/**
 * UI Editor Logic
 */

// --- DOM Elements ---
const drawingArea = document.getElementById('drawing-area');
const canvasContent = document.getElementById('canvas-content');
const propertiesContent = document.getElementById('properties-content');

// Carousels
const editGrid = document.getElementById('edit-grid');
const toolsGrid = document.getElementById('tools-grid');

const btnEditLeft = document.getElementById('btn-edit-left');
const btnEditRight = document.getElementById('btn-edit-right');
const btnMoveLeft = document.getElementById('btn-move-left');
const btnMoveRight = document.getElementById('btn-move-right');

const fileInput = document.getElementById('file-input');
const textInputTemplate = document.getElementById('text-input-template');

// --- State ---
const COMPONENT_TOOLS = [
    { id: 'button', icon: '🖱️', label: 'Button' },
    { id: 'text', icon: '📝', label: 'Text' },
    { id: 'input', icon: '🔤', label: 'Input' },
    { id: 'align', icon: '📐', label: 'Left Align' },
    { id: 'top-align', icon: '⬆️', label: 'Top Align' }
];

// Edit Actions: Save, Load, Reset, Delete, Move
// We need objects to manage carousel rendering
const EDIT_TOOLS = [
    { id: 'save', icon: '💾', label: 'Save', type: 'action' },
    { id: 'load', icon: '📂', label: 'Load', type: 'action' },
    { id: 'reset', icon: '🔄', label: 'Reset', type: 'action' },
    { id: 'delete', icon: '🗑️', label: 'Delete', type: 'toggle' },
    { id: 'move', icon: '🖐️', label: 'Move', type: 'toggle' }
];

let toolState = {
    currentTool: null, // 'button' | 'text' | 'input' | 'align' | 'top-align' | null
    isDrawing: false,
    startX: 0,
    startY: 0,
    ghostBox: null,
    currentTextValue: "",

    // Component Nav
    compStartIndex: 0,
    compPageSize: 3,

    // Edit Nav
    editStartIndex: 0,
    editPageSize: 3,

    // Panning
    panOffset: { x: 0, y: 0 },
    isPanning: false,
    panStartX: 0,
    panStartY: 0,

    // Modes
    deleteMode: false,
    moveMode: false,

    // Moving Elements
    isMovingElement: false,
    movingElement: null,
    moveOffsetX: 0,
    moveOffsetY: 0
};

// --- Initialization ---

function init() {
    renderComponentTools();
    renderEditTools();
    updateNavButtons();
}

// --- Navigation & Rendering ---

// 1. Component Tools
function renderComponentTools() {
    toolsGrid.innerHTML = '';
    const visible = COMPONENT_TOOLS.slice(toolState.compStartIndex, toolState.compStartIndex + toolState.compPageSize);

    visible.forEach(tool => {
        const btn = document.createElement('button');
        btn.classList.add('tool-btn');
        if (toolState.currentTool === tool.id) btn.classList.add('active');
        btn.innerHTML = `<span class="icon">${tool.icon}</span><span class="label">${tool.label}</span>`;
        btn.onclick = () => selectTool(tool.id);

        // Disable if modes active
        if (toolState.deleteMode || toolState.moveMode) btn.disabled = true;

        toolsGrid.appendChild(btn);
    });
}

// 2. Edit Tools
function renderEditTools() {
    editGrid.innerHTML = '';
    const visible = EDIT_TOOLS.slice(toolState.editStartIndex, toolState.editStartIndex + toolState.editPageSize);

    visible.forEach(tool => {
        const btn = document.createElement('button');
        btn.classList.add('action-btn');
        btn.disabled = false; // Default enable

        // Specific styling hooks or Icons
        // We'll regenerate innerHTML based on ID to match SVG style or emojis
        let iconHtml = tool.icon;
        // Use SVG for consistency if preferred, but emoji is easier for new items. Plan used symbols.
        if (tool.id === 'save') {
            iconHtml = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>`;
        } else if (tool.id === 'load') {
            iconHtml = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`;
        } else if (tool.id === 'reset') {
            iconHtml = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>`;
        }
        // Delete/Move use simple SVGs or just emoji is fine. Restored SVG for Delete.
        if (tool.id === 'delete') {
            iconHtml = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;
        }
        if (tool.id === 'move') {
            iconHtml = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 7l4-4 4 4M16 17l-4 4-4-4M16 7l-4-4-4 4M8 17l4 4 4-4M4 12h16M12 4v16"></path></svg>`;
        }

        btn.innerHTML = `${iconHtml} ${tool.label}`;
        btn.onclick = () => handleEditAction(tool.id);

        // Active States
        if (tool.id === 'delete' && toolState.deleteMode) btn.classList.add('active');
        if (tool.id === 'move' && toolState.moveMode) btn.classList.add('active');

        // Logic for disabling buttons based on modes
        // "toggle ... set all other buttons ... to non-interactive"
        if (toolState.deleteMode) {
            if (tool.id !== 'delete') btn.disabled = true;
        }
        if (toolState.moveMode) {
            // "Pressing this button will make all other buttons interactive [SIC - inactive]"
            // Usually this implies Move is the ONLY active thing.
            if (tool.id !== 'move') btn.disabled = true;
        }

        editGrid.appendChild(btn);
    });
}

function updateNavButtons() {
    // Component Nav
    btnMoveLeft.disabled = toolState.compStartIndex === 0 || toolState.deleteMode || toolState.moveMode;
    const maxComp = Math.max(0, COMPONENT_TOOLS.length - toolState.compPageSize);
    btnMoveRight.disabled = toolState.compStartIndex >= maxComp || toolState.deleteMode || toolState.moveMode;

    // Edit Nav
    btnEditLeft.disabled = toolState.editStartIndex === 0; // Nav should stay active or disabled? "make all other buttons interactive"? Let's disable to be safe.
    if (toolState.deleteMode || toolState.moveMode) btnEditLeft.disabled = true;

    const maxEdit = Math.max(0, EDIT_TOOLS.length - toolState.editPageSize);
    btnEditRight.disabled = toolState.editStartIndex >= maxEdit;
    if (toolState.deleteMode || toolState.moveMode) btnEditRight.disabled = true;
}

// Nav Handlers
btnMoveLeft.click = () => { }; // Rebind via addEventListener below
btnMoveLeft.addEventListener('click', () => { if (toolState.compStartIndex > 0) { toolState.compStartIndex--; refreshAll(); } });
btnMoveRight.addEventListener('click', () => { const max = COMPONENT_TOOLS.length - toolState.compPageSize; if (toolState.compStartIndex < max) { toolState.compStartIndex++; refreshAll(); } });

btnEditLeft.addEventListener('click', () => { if (toolState.editStartIndex > 0) { toolState.editStartIndex--; refreshAll(); } });
btnEditRight.addEventListener('click', () => { const max = EDIT_TOOLS.length - toolState.editPageSize; if (toolState.editStartIndex < max) { toolState.editStartIndex++; refreshAll(); } });

function refreshAll() {
    renderComponentTools();
    renderEditTools();
    updateNavButtons();
}

// --- Action Logic ---

function handleEditAction(actionId) {
    if (actionId === 'save') doSave();
    if (actionId === 'load') doLoad();
    if (actionId === 'reset') doReset();
    if (actionId === 'delete') toggleDelete();
    if (actionId === 'move') toggleMove();
}

function doReset() {
    // 1. Reset Pan
    toolState.panOffset = { x: 0, y: 0 };
    updateCanvasTransform();

    // 2. Smart Reset
    const elements = canvasContent.querySelectorAll('.canvas-element');
    let minTop = Infinity;
    let minLeft = Infinity;
    elements.forEach(el => {
        const top = parseInt(el.style.top);
        const left = parseInt(el.style.left);
        if (top < minTop) minTop = top;
        if (left < minLeft) minLeft = left;
    });

    let shiftY = 0;
    let shiftX = 0;
    if (minTop < 5 && minTop !== Infinity) shiftY = 5 - minTop;
    if (minLeft < 5 && minLeft !== Infinity) shiftX = 5 - minLeft;

    if (shiftX !== 0 || shiftY !== 0) {
        elements.forEach(el => {
            el.style.top = `${parseInt(el.style.top) + shiftY}px`;
            el.style.left = `${parseInt(el.style.left) + shiftX}px`;
        });
    }
}

function toggleDelete() {
    toolState.deleteMode = !toolState.deleteMode;
    if (toolState.deleteMode) {
        // Disable Move if active
        toolState.moveMode = false;
        resetTool(); // Clear any drawing tools
    }
    refreshAll();
}

function toggleMove() {
    toolState.moveMode = !toolState.moveMode;
    if (toolState.moveMode) {
        // Disable Delete if active
        toolState.deleteMode = false;
        resetTool();
    }
    refreshAll();
}

// --- Tool Selection (Component Area) ---

function selectTool(toolId) {
    if (toolState.currentTool === toolId) {
        resetTool();
        return;
    }
    toolState.currentTool = toolId;
    toolState.alignMode = (toolId === 'align' || toolId === 'top-align');

    refreshAll();
    updatePropertiesArea(toolId);
}

function resetTool() {
    toolState.currentTool = null;
    toolState.alignMode = false;
    toolState.isDrawing = false;
    if (toolState.ghostBox) {
        toolState.ghostBox.remove();
        toolState.ghostBox = null;
    }
    refreshAll();
    updatePropertiesArea(null);
}

function updatePropertiesArea(toolId) {
    propertiesContent.innerHTML = '';
    if (toolId === 'text' || toolId === 'input') {
        const clone = textInputTemplate.content.cloneNode(true);
        propertiesContent.appendChild(clone);
        const textarea = propertiesContent.querySelector('textarea');
        textarea.value = toolState.currentTextValue;
        textarea.addEventListener('input', (e) => {
            toolState.currentTextValue = e.target.value;
        });
        textarea.focus();
    } else if (toolId === 'button') {
        propertiesContent.innerHTML = '<p class="placeholder-text">Drag to create Button.</p>';
    } else if (toolId === 'align') {
        propertiesContent.innerHTML = '<p class="placeholder-text">Click canvas to Left Align elements.</p>';
    } else if (toolId === 'top-align') {
        propertiesContent.innerHTML = '<p class="placeholder-text">Click canvas to Top Align elements.</p>';
    } else {
        propertiesContent.innerHTML = '<p class="placeholder-text">Select a component to configure.</p>';
    }
}

// --- Interactions ---

drawingArea.addEventListener('mousedown', (e) => {
    // 1. Panning - ONLY if Background click and NOT moving an element
    // Check target: if dragging an element in move mode, handle separately relative to element
    // Actually using element listeners for move start is better.

    if (toolState.isDrawing || toolState.isMovingElement) return;

    // Check if background
    // If clicking element in Move Mode, propagation stops in element listener?
    // Or we check target here.
    if (e.target.closest('.canvas-element')) return;

    // 2. Align Click handles
    // 3. Drawing handles
    if (toolState.currentTool && !toolState.alignMode) {
        startDrawing(e);
    } else if (!toolState.currentTool && !toolState.deleteMode && !toolState.moveMode && !toolState.alignMode) {
        // Pan default
        startPanning(e);
    }
});

// Move Tool Logic - Element Listeners
// We need to attach listeners to elements when created/loaded
function attachElementListeners(el) {
    el.addEventListener('mousedown', (e) => {
        // Delete Mode
        if (toolState.deleteMode) {
            e.stopPropagation();
            el.remove();
            return;
        }

        // Move Mode
        if (toolState.moveMode) {
            e.stopPropagation(); // Don't trigger canvas panning
            startMoveElement(e, el);
        }
    });
}

function startMoveElement(e, el) {
    toolState.isMovingElement = true;
    toolState.movingElement = el;
    el.classList.add('moving');

    const rect = el.getBoundingClientRect();
    // Offset from element top-left
    toolState.moveOffsetX = e.clientX - rect.left;
    toolState.moveOffsetY = e.clientY - rect.top;
}

function startDrawing(e) {
    toolState.isDrawing = true;
    const rect = drawingArea.getBoundingClientRect();
    toolState.startX = e.clientX - rect.left;
    toolState.startY = e.clientY - rect.top;

    toolState.ghostBox = document.createElement('div');
    toolState.ghostBox.classList.add('ghost-box');
    toolState.ghostBox.style.left = `${toolState.startX}px`;
    toolState.ghostBox.style.top = `${toolState.startY}px`;
    toolState.ghostBox.style.width = '0px';
    toolState.ghostBox.style.height = '0px';
    drawingArea.appendChild(toolState.ghostBox);
}

function startPanning(e) {
    toolState.isPanning = true;
    toolState.panStartX = e.clientX;
    toolState.panStartY = e.clientY;
    drawingArea.style.cursor = 'grabbing';
}

window.addEventListener('mousemove', (e) => {
    // 1. Drawing
    if (toolState.isDrawing && toolState.ghostBox) {
        const rect = drawingArea.getBoundingClientRect();
        const currentX = Math.min(Math.max(0, e.clientX - rect.left), rect.width);
        const currentY = Math.min(Math.max(0, e.clientY - rect.top), rect.height);

        const width = Math.abs(currentX - toolState.startX);
        const height = Math.abs(currentY - toolState.startY);
        const left = Math.min(toolState.startX, currentX);
        const top = Math.min(toolState.startY, currentY);

        toolState.ghostBox.style.width = `${width}px`;
        toolState.ghostBox.style.height = `${height}px`;
        toolState.ghostBox.style.left = `${left}px`;
        toolState.ghostBox.style.top = `${top}px`;
    }

    // 2. panning
    if (toolState.isPanning) {
        const dx = e.clientX - toolState.panStartX;
        const dy = e.clientY - toolState.panStartY;
        toolState.panOffset.x += dx;
        toolState.panOffset.y += dy;
        toolState.panStartX = e.clientX;
        toolState.panStartY = e.clientY;
        updateCanvasTransform();
    }

    // 3. Moving Element
    if (toolState.isMovingElement && toolState.movingElement) {
        const rect = drawingArea.getBoundingClientRect();
        // Mouse relative to drawing area
        const clientX = e.clientX - rect.left;
        const clientY = e.clientY - rect.top;

        // Convert to World Coordinates (subtract Pan)
        const worldX = clientX - toolState.panOffset.x;
        const worldY = clientY - toolState.panOffset.y;

        // Apply Offset (so we drag from where we clicked)
        const finalX = worldX - toolState.moveOffsetX;
        const finalY = worldY - toolState.moveOffsetY;

        toolState.movingElement.style.left = `${finalX}px`;
        toolState.movingElement.style.top = `${finalY}px`;
    }
});

window.addEventListener('mouseup', (e) => {
    if (toolState.isDrawing) finishDrawing();
    if (toolState.isPanning) {
        toolState.isPanning = false;
        drawingArea.style.cursor = 'default';
    }
    if (toolState.isMovingElement) {
        toolState.isMovingElement = false;
        if (toolState.movingElement) {
            toolState.movingElement.classList.remove('moving');
            toolState.movingElement = null;
        }
    }
});

function updateCanvasTransform() {
    canvasContent.style.transform = `translate(${toolState.panOffset.x}px, ${toolState.panOffset.y}px)`;
}

function finishDrawing() {
    toolState.isDrawing = false;
    const width = parseInt(toolState.ghostBox.style.width);
    const height = parseInt(toolState.ghostBox.style.height);
    const boxLeft = parseInt(toolState.ghostBox.style.left);
    const boxTop = parseInt(toolState.ghostBox.style.top);

    toolState.ghostBox.remove();
    toolState.ghostBox = null;

    if (width > 5 && height > 5) {
        const worldLeft = boxLeft - toolState.panOffset.x;
        const worldTop = boxTop - toolState.panOffset.y;
        createElement(toolState.currentTool, { left: worldLeft, top: worldTop, width, height });
    }
    resetTool();
}

function createElement(type, coords) {
    let el;
    if (type === 'button') el = document.createElement('button');
    else if (type === 'input') el = document.createElement('input');
    else el = document.createElement('div');

    el.classList.add('canvas-element');

    if (type === 'button') el.classList.add('button-element');
    else if (type === 'input') el.classList.add('input-element');
    else el.classList.add('text-element');

    el.style.left = `${coords.left}px`;
    el.style.top = `${coords.top}px`;
    el.style.width = `${coords.width}px`;
    el.style.height = `${coords.height}px`;

    if (type === 'button') el.textContent = "Button";
    else if (type === 'text') el.innerText = toolState.currentTextValue || "Please enter text here";
    else if (type === 'input') el.value = toolState.currentTextValue || "Input";

    attachElementListeners(el); // IMPORTANT: Moving & Deleting logic
    canvasContent.appendChild(el);
}

// Align Click Logic
drawingArea.addEventListener('click', (e) => {
    if (!toolState.alignMode) return;
    if (e.target.closest('.canvas-element')) return;

    const rect = drawingArea.getBoundingClientRect();
    const clickXView = e.clientX - rect.left;
    const clickYView = e.clientY - rect.top;

    const clickXWorld = clickXView - toolState.panOffset.x;
    const clickYWorld = clickYView - toolState.panOffset.y;

    if (toolState.currentTool === 'align') {
        const line = document.createElement('div');
        line.classList.add('alignment-line');
        line.style.left = `${clickXWorld}px`;
        canvasContent.appendChild(line);

        canvasContent.querySelectorAll('.canvas-element').forEach(el => {
            const elLeft = parseInt(el.style.left);
            if (elLeft > clickXWorld && elLeft < (clickXWorld + 20)) {
                el.style.left = `${clickXWorld}px`;
            }
        });
        setTimeout(() => { line.remove(); resetTool(); }, 500);
    } else if (toolState.currentTool === 'top-align') {
        const line = document.createElement('div');
        line.classList.add('alignment-line-horizontal');
        line.style.top = `${clickYWorld}px`;
        canvasContent.appendChild(line);

        canvasContent.querySelectorAll('.canvas-element').forEach(el => {
            const elTop = parseInt(el.style.top);
            if (elTop > clickYWorld && elTop < (clickYWorld + 20)) {
                el.style.top = `${clickYWorld}px`;
            }
        });
        setTimeout(() => { line.remove(); resetTool(); }, 500);
    }
});

// --- Save / Load Helpers ---
function doSave() {
    const elements = canvasContent.querySelectorAll('.canvas-element');
    let htmlContent = '';
    let cssContent = '';

    elements.forEach((el, index) => {
        const id = `el-${Date.now()}-${index}`;
        const tagName = el.tagName.toLowerCase();
        const isInput = (tagName === 'input');

        let tagHtml = '';
        if (isInput) tagHtml = `<${tagName} id="${id}" class="ui-element" value="${el.value}">`;
        else tagHtml = `<${tagName} id="${id}" class="ui-element">${el.textContent}</${tagName}>`;

        htmlContent += `${tagHtml}\n`;

        cssContent += `#${id} {
    position: absolute;
    left: ${el.style.left};
    top: ${el.style.top};
    width: ${el.style.width};
    height: ${el.style.height};
    ${(tagName === 'button') ? 'background-color: #6c5ce7; color: white; border: none; border-radius: 4px;' :
                (isInput) ? 'background-color: #2a2e37; color: white; border: 1px solid #333642; border-radius: 4px; padding: 4px 8px;' :
                    'background: transparent; color: inherit; white-space: pre-wrap;'}
}\n`;
    });

    const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated UI</title>
    <link rel="stylesheet" href="style.css">
    <style> body { margin: 0; height: 100vh; } </style>
</head>
<body>
    <div id="ui-container" style="position: relative; width: 100%; height: 100%;">
        ${htmlContent}
    </div>
</body>
</html>`;

    downloadFile('layout.html', fullHtml);
    downloadFile('style.css', `/* Generated Styles */\n.ui-element { box-sizing: border-box; }\n${cssContent}`);
}

function doLoad() {
    fileInput.value = '';
    fileInput.click();
}

function downloadFile(filename, content) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

fileInput.addEventListener('change', async (e) => {
    const files = Array.from(e.target.files);
    const htmlFile = files.find(f => f.name.endsWith('.html'));
    const cssFile = files.find(f => f.name.endsWith('.css'));

    if (htmlFile && cssFile) {
        const htmlText = await readFile(htmlFile);
        const cssText = await readFile(cssFile);
        loadLayout(htmlText, cssText);
    }
});

function readFile(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsText(file);
    });
}

function loadLayout(html, css) {
    canvasContent.innerHTML = '';
    toolState.panOffset = { x: 0, y: 0 };
    updateCanvasTransform();

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    const container = tempDiv.querySelector('#ui-container') || tempDiv.querySelector('div');

    if (container) {
        Array.from(container.children).forEach(child => {
            const type = child.tagName.toLowerCase();
            const newEl = document.createElement(type);
            newEl.id = child.id;

            newEl.classList.add('canvas-element');
            if (type === 'button') {
                newEl.classList.add('button-element');
                newEl.textContent = child.textContent;
            } else if (type === 'input') {
                newEl.classList.add('input-element');
                newEl.value = child.value;
            } else {
                newEl.classList.add('text-element');
                newEl.textContent = child.textContent;
            }

            attachElementListeners(newEl);
            canvasContent.appendChild(newEl);
        });
    }

    const styleId = 'loaded-styles';
    let styleTag = document.getElementById(styleId);
    if (styleTag) styleTag.remove();

    styleTag = document.createElement('style');
    styleTag.id = styleId;
    styleTag.textContent = css;
    document.head.appendChild(styleTag);

    setTimeout(() => {
        const sheet = styleTag.sheet;
        const rules = sheet.cssRules || sheet.rules;
        Array.from(rules).forEach(rule => {
            if (rule.selectorText.startsWith('#el-')) {
                const el = document.getElementById(rule.selectorText.slice(1));
                if (el) {
                    el.style.left = rule.style.left;
                    el.style.top = rule.style.top;
                    el.style.width = rule.style.width;
                    el.style.height = rule.style.height;
                }
            }
        });
        styleTag.remove();
    }, 100);
}

// Start
init();
