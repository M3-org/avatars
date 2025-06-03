// CACHE BUST: 2024-12-19-15:30 - Force browser to reload this file
// Global variables
let charactersData = {};
let isCompactView = false;
let isMusicPlaying = false;
let isSoundEnabled = true;
let isDarkMode = false;
let selectedCharacter = null;

// Detect base path for GitHub Pages compatibility
function getBasePath() {
    const path = window.location.pathname;
    const hostname = window.location.hostname;
    const port = window.location.port;
    console.log('=== PATH DETECTION DEBUG v2 ===');
    console.log('Current pathname:', path);
    console.log('Current hostname:', hostname);
    console.log('Current port:', port);
    
    // Force Prepros detection for port 8848
    if (port === '8848' || hostname === 'localhost' || hostname === '127.0.0.1') {
        console.log('PREPROS DETECTED v2 - Using relative parent path');
        // Character folders are in parent directory of character-select
        return '../';
    }
    
    // For GitHub Pages or other hosting
    if (path.includes('/avatars/character-select/')) {
        console.log('GitHub Pages - character-select detected, using ../');
        return '../';
    } else if (path.includes('/avatars/')) {
        console.log('GitHub Pages - avatars root, using ./');
        return './';
    } else if (path.includes('/character-select/')) {
        console.log('Generic hosting - character-select detected, using ../');
        return '../';
    } else {
        console.log('Default fallback, using ./');
        return './';
    }
}

const BASE_PATH = '../'; // FORCE CORRECT PATH FOR PREPROS
console.log('FORCED BASE_PATH set to:', BASE_PATH);
console.log('Sample image path would be:', BASE_PATH + '0g/thumb-bust_0g.png');

// DOM elements
const loadingScreen = document.getElementById('loadingScreen');
const loadingProgress = document.getElementById('loadingProgress');
const characterGrid = document.getElementById('characterGrid');
const characterModal = document.getElementById('characterModal');
const closeModal = document.getElementById('closeModal');
const musicToggle = document.getElementById('musicToggle');
const soundToggle = document.getElementById('soundToggle');
const viewToggle = document.getElementById('viewToggle');
const darkModeToggle = document.getElementById('darkModeToggle');
const bgMusic = document.getElementById('bgMusic');

// Sound effect elements
const hoverSound = document.getElementById('hoverSound');
const selectSound = document.getElementById('selectSound');
const closeSound = document.getElementById('closeSound');

// Character detail elements
const characterLargeImage = document.getElementById('characterLargeImage');
const characterGLBImage = document.getElementById('characterGLBImage');
const characterName = document.getElementById('characterName');
const characterType = document.getElementById('characterType');
const characterBio = document.getElementById('characterBio');
const characterFiles = document.getElementById('characterFiles');
const viewGLB = document.getElementById('viewGLB');
const viewVRM = document.getElementById('viewVRM');
const exportJSON = document.getElementById('exportJSON');

// Copy button elements
const copyBio = document.getElementById('copyBio');

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadCharacters();
        setupEventListeners();
        setupSoundEffects();
        hideLoadingScreen();
    } catch (error) {
        console.error('Failed to initialize application:', error);
        hideLoadingScreen();
    }
});

// Load character data - simplified approach
async function loadCharacters() {
    try {
        updateLoadingProgress(10, 'Loading character data...');
        
        // Try to load from data.json first (most reliable)
        await loadFromDataJSON();
        
    } catch (error) {
        console.error('Error loading characters:', error);
        // If data.json fails, try CSV approach
        try {
            await loadFromCSV();
        } catch (csvError) {
            console.error('CSV loading also failed:', csvError);
            // Final fallback: create characters from directory structure
            await loadFromDirectoryStructure();
        }
    }
}

// Load from data.json (primary method)
async function loadFromDataJSON() {
    try {
        updateLoadingProgress(20, 'Loading from data.json...');
        
        const response = await fetch('../data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const jsonData = await response.json();
        updateLoadingProgress(50, 'Processing character data...');
        
        // Convert data.json format to our expected format
        charactersData = {};
        for (const [key, data] of Object.entries(jsonData)) {
            charactersData[key] = {
                name: key,
                bust_thumb: data.bust_thumb || BASE_PATH + `${key}/thumb-bust_${key}.png`,
                bust_image: data.bust || BASE_PATH + `${key}/bust_${key}.png`,
                glb_thumb: data.glb_thumb || BASE_PATH + `${key}/thumb-glb_${key}.png`,
                glb_image: data.glb_preview || data.glb_thumb || BASE_PATH + `${key}/glb_${key}.png`,
                glb: data.glb || BASE_PATH + `${key}/${key}.glb`,
                vrm: data.vrm || BASE_PATH + `${key}/${key}.vrm`,
                bio: data.bio
            };
        }
        
        console.log(`✅ Loaded ${Object.keys(charactersData).length} characters from data.json`);
        
        updateLoadingProgress(70, 'Loading character images...');
        await renderCharacters();
        updateLoadingProgress(100, 'Ready!');
        
    } catch (error) {
        console.error('Error loading from data.json:', error);
        throw error;
    }
}

// Load from CSV (fallback method)
async function loadFromCSV() {
    try {
        updateLoadingProgress(20, 'Loading from CSV...');
        
        const csvResponse = await fetch('../avatars.csv');
        if (!csvResponse.ok) {
            throw new Error(`HTTP error! status: ${csvResponse.status}`);
        }
        
        const csvText = await csvResponse.text();
        const characterNames = parseCSV(csvText);
        
        updateLoadingProgress(40, 'Processing character files...');
        
        // Build character data from file structure
        charactersData = {};
        for (const name of characterNames) {
            if (name && name.trim()) {
                charactersData[name] = await buildCharacterData(name);
            }
        }
        
        updateLoadingProgress(70, 'Loading character images...');
        await renderCharacters();
        updateLoadingProgress(100, 'Ready!');
        
    } catch (error) {
        console.error('Error loading from CSV:', error);
        throw error;
    }
}

// Load from directory structure (final fallback)
async function loadFromDirectoryStructure() {
    updateLoadingProgress(30, 'Creating basic fallback characters...');
    
    // Known working characters (excluding problematic ones)
    const knownCharacters = [
        '0g', '8ball', 'aave', 'aavegotchi', 'arbitrum', 'aura', 'balancer', 'beam', 
        'beff-ai', 'berachain', 'celestia', 'collab-land', 'compound', 'cowdao', 'curve', 
        'dydx', 'eigenlayer', 'eliza', 'ens', 'etherfi', 'euler', 'flashbots', 'fluid', 
        'frax', 'fuel', 'gitcoin', 'gmx', 'gnon', 'gnosis', 'hyperfy', 'jupiter', 'lido', 
        'magic-eden', 'marc', 'moonwell', 'morpho', 'nifty-island', 'octant', 'optimism', 
        'paladin', 'peepo', 'polygon', 'reserve', 'rocketpool', 'ropraito', 'safe', 
        'scroll', 'shaw-ai', 'sky', 'soleng', 'spartan', 'spectra', 'superfluid', 
        'the-graph', 'tron', 'uniswap', 'venus', 'vitalik', 'zerebro'
    ];
    
    charactersData = {};
    for (const name of knownCharacters) {
        charactersData[name] = {
            name: name,
            bust_thumb: BASE_PATH + `${name}/thumb-bust_${name}.png`,
            bust_image: BASE_PATH + `${name}/bust_${name}.png`,
            glb_thumb: BASE_PATH + `${name}/thumb-glb_${name}.png`,
            glb_image: BASE_PATH + `${name}/glb_${name}.png`,
            glb: BASE_PATH + `${name}/${name}.glb`,
            vrm: BASE_PATH + `${name}/${name}.vrm`,
            bio: `# ${name.replace(/-/g, ' ').toUpperCase()}\n\nCrypto character from the avatar collection.`
        };
    }
    
    console.log(`✅ Created ${Object.keys(charactersData).length} basic fallback characters`);
    console.log(`⚠️  Note: Rich bio content requires data.json to load properly`);
    
    updateLoadingProgress(70, 'Loading character images...');
    await renderCharacters();
    updateLoadingProgress(100, 'Ready!');
}

// Parse CSV to get character names
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const names = [];
    
    // Characters to exclude (known to have missing assets)
    const excludeList = ['emblem-vault', 'heurist'];
    
    // Skip header line, get first column (character names)
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
            const columns = line.split(',');
            const name = columns[0].trim().replace(/"/g, ''); // Remove quotes
            
            // Only include characters that:
            // 1. Have a name
            // 2. Are not in the exclude list
            // 3. Have at least a bust thumbnail (column 2)
            const bustThumbnail = columns[1] ? columns[1].trim() : '';
            
            if (name && 
                name !== '' && 
                !excludeList.includes(name) && 
                bustThumbnail && 
                bustThumbnail !== '') {
                names.push(name);
            }
        }
    }
    
    return names;
}

// Build character data from file structure
async function buildCharacterData(name) {
    const character = {
        name: name,
        bust_thumb: BASE_PATH + `${name}/thumb-bust_${name}.png`,
        bust_image: BASE_PATH + `${name}/bust_${name}.png`,
        glb_thumb: BASE_PATH + `${name}/thumb-glb_${name}.png`,
        glb_image: BASE_PATH + `${name}/glb_${name}.png`,
        glb: BASE_PATH + `${name}/${name}.glb`,
        vrm: BASE_PATH + `${name}/${name}.vrm`,
        bio: null
    };
    
    // Try to load the markdown bio
    try {
        const bioResponse = await fetch(`../${name}/${name}.md`);
        if (bioResponse.ok) {
            character.bio = await bioResponse.text();
        }
    } catch (error) {
        // Silently handle bio loading errors
        character.bio = `# ${name.replace(/-/g, ' ').toUpperCase()}\n\nCrypto character from the avatar collection.`;
    }
    
    return character;
}

// Render character grid
async function renderCharacters() {
    const characters = Object.entries(charactersData);
    const totalCharacters = characters.length;
    let loadedCharacters = 0;

    characterGrid.innerHTML = '';

    for (const [key, character] of characters) {
        // Skip characters without thumbnails
        if (!character.bust_thumb) {
            loadedCharacters++;
            continue;
        }

        const characterCard = createCharacterCard(key, character);
        characterGrid.appendChild(characterCard);
        
        loadedCharacters++;
        const progress = 70 + (loadedCharacters / totalCharacters) * 30;
        updateLoadingProgress(progress, `Loading ${key}...`);
        
        // Small delay to show loading progress
        await new Promise(resolve => setTimeout(resolve, 30));
    }
}

// Create individual character card
function createCharacterCard(key, character) {
    const card = document.createElement('div');
    card.className = 'character-card';
    card.dataset.character = key;
    
    // Create card actions (copy and export buttons)
    const cardActions = document.createElement('div');
    cardActions.className = 'card-actions';
    
    // Copy button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'card-action-btn copy';
    copyBtn.innerHTML = '📋';
    copyBtn.title = 'Copy bio';
    copyBtn.onclick = async (e) => {
        e.stopPropagation(); // Prevent card click
        playSelectSound();
        
        let bioText = '';
        if (character.bio) {
            bioText = character.bio
                .replace(/^#+\s*/gm, '')
                .replace(/\*\*(.*?)\*\*/g, '$1')
                .replace(/\*(.*?)\*/g, '$1')
                .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
                .replace(/^\- /gm, '• ')
                .replace(/\n\s*\n/g, '\n\n')
                .trim();
        } else {
            bioText = `${(character.name || key).replace(/-/g, ' ').replace(/_/g, ' ')}\n\nNo bio available for this character yet.`;
        }
        
        await copyToClipboard(bioText, copyBtn);
    };
    
    // Export button
    const exportBtn = document.createElement('button');
    exportBtn.className = 'card-action-btn export';
    exportBtn.innerHTML = '📄';
    exportBtn.title = 'Export JSON';
    exportBtn.onclick = (e) => {
        e.stopPropagation(); // Prevent card click
        playSelectSound();
        exportCharacterData(key, character);
        
        // Visual feedback
        const originalText = exportBtn.innerHTML;
        exportBtn.innerHTML = '✅';
        setTimeout(() => {
            exportBtn.innerHTML = originalText;
        }, 2000);
    };
    
    cardActions.appendChild(copyBtn);
    cardActions.appendChild(exportBtn);
    
    // Create thumbnail image
    const thumbnail = document.createElement('img');
    thumbnail.className = 'character-thumbnail';
    
    // DEBUG: Log the image path construction
    console.log(`=== IMAGE DEBUG for ${key} ===`);
    console.log('character.bust_thumb:', character.bust_thumb);
    console.log('BASE_PATH:', BASE_PATH);
    console.log('Final thumbnail src will be:', character.bust_thumb);
    
    thumbnail.src = character.bust_thumb;
    thumbnail.alt = character.name || key;
    thumbnail.loading = 'lazy';
    
    // DEBUG: Log what the browser actually requests
    thumbnail.addEventListener('load', () => {
        console.log(`✅ SUCCESS loading: ${thumbnail.src}`);
    });
    
    thumbnail.addEventListener('error', () => {
        console.log(`❌ FAILED loading: ${thumbnail.src}`);
        console.log('Browser resolved this to:', thumbnail.src);
    });
    
    // Handle image load errors with fallbacks (silently)
    thumbnail.onerror = () => {
        // Try alternative paths without console spam
        const fallbacks = [
            character.bust_image, // Try the full bust image as fallback
            BASE_PATH + `${key}/bust_${key}.png`,
            BASE_PATH + `${key}/${key}.png`
        ];
        
        let currentFallback = 0;
        const tryNextFallback = () => {
            if (currentFallback < fallbacks.length) {
                thumbnail.src = fallbacks[currentFallback];
                currentFallback++;
            } else {
                // Final fallback: hide the card if no images work
                card.style.display = 'none';
            }
        };
        
        thumbnail.onerror = tryNextFallback;
        tryNextFallback();
    };
    
    // Create character name
    const name = document.createElement('div');
    name.className = 'character-card-name';
    name.textContent = (character.name || key).replace(/-/g, ' ').replace(/_/g, ' ');
    
    card.appendChild(cardActions);
    card.appendChild(thumbnail);
    card.appendChild(name);
    
    // Add hover sound effect
    card.addEventListener('mouseenter', () => {
        playHoverSound();
    });
    
    // Add click event with selection sound
    card.addEventListener('click', () => {
        playSelectSound();
        
        // Remove selected class from previously selected character
        if (selectedCharacter) {
            selectedCharacter.classList.remove('selected');
        }
        
        // Add selected class to current character
        card.classList.add('selected');
        selectedCharacter = card;
        
        openCharacterModal(key, character);
    });
    
    return card;
}

// Open character detail modal
function openCharacterModal(key, character) {
    // Set character bust image - use bust image for larger view
    characterLargeImage.src = character.bust_image || character.bust_thumb;
    characterLargeImage.alt = `${character.name || key} - Bust`;
    
    // Set character GLB preview image
    characterGLBImage.src = character.glb_image || character.glb_thumb || character.bust_image || character.bust_thumb;
    characterGLBImage.alt = `${character.name || key} - 3D Model`;
    
    // Handle bust image load errors with fallbacks
    characterLargeImage.onerror = () => {
        const fallbacks = [
            character.bust_thumb,
            BASE_PATH + `${key}/bust_${key}.png`,
            BASE_PATH + `${key}/${key}.png`
        ];
        
        let currentFallback = 0;
        const tryNextFallback = () => {
            if (currentFallback < fallbacks.length) {
                characterLargeImage.src = fallbacks[currentFallback];
                currentFallback++;
            } else {
                // Final fallback: use a simple colored div
                characterLargeImage.style.display = 'none';
            }
        };
        
        characterLargeImage.onerror = tryNextFallback;
        tryNextFallback();
    };
    
    // Handle GLB image load errors with fallbacks
    characterGLBImage.onerror = () => {
        const glbFallbacks = [
            character.glb_thumb,
            BASE_PATH + `${key}/glb_${key}.png`,
            character.bust_image,
            character.bust_thumb
        ];
        
        let currentGLBFallback = 0;
        const tryNextGLBFallback = () => {
            if (currentGLBFallback < glbFallbacks.length) {
                characterGLBImage.src = glbFallbacks[currentGLBFallback];
                currentGLBFallback++;
            } else {
                // Final fallback: hide GLB image if nothing works
                characterGLBImage.style.display = 'none';
            }
        };
        
        characterGLBImage.onerror = tryNextGLBFallback;
        tryNextGLBFallback();
    };
    
    // Set character name
    characterName.textContent = (character.name || key).replace(/-/g, ' ').replace(/_/g, ' ');
    
    // Set character type based on bio content
    const type = getCharacterType(character.bio);
    characterType.textContent = type;
    
    // Set character bio
    characterBio.innerHTML = parseMarkdown(character.bio || `# ${character.name || key}\n\nNo bio available for this character yet.`);
    
    // Setup action buttons
    setupActionButtons(character);
    
    // Setup copy and export functionality
    setupCopyAndExport(key, character);
    
    // Show modal
    characterModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Close character modal
function closeCharacterModal() {
    playCloseSound();
    characterModal.classList.remove('active');
    document.body.style.overflow = '';
    
    // Clear selected state after a short delay for visual feedback
    setTimeout(() => {
        if (selectedCharacter) {
            selectedCharacter.classList.remove('selected');
            selectedCharacter = null;
        }
    }, 300);
}

// Get character type from bio
function getCharacterType(bio) {
    if (!bio) return 'Crypto Entity';
    
    const bioLower = bio.toLowerCase();
    
    if (bioLower.includes('defi') || bioLower.includes('lending') || bioLower.includes('trading')) {
        return 'DeFi Protocol';
    } else if (bioLower.includes('ai') || bioLower.includes('artificial intelligence')) {
        return 'AI Agent';
    } else if (bioLower.includes('layer') || bioLower.includes('blockchain') || bioLower.includes('chain')) {
        return 'Blockchain Infrastructure';
    } else if (bioLower.includes('nft') || bioLower.includes('gaming') || bioLower.includes('metaverse')) {
        return 'Gaming/NFT';
    } else if (bioLower.includes('staking') || bioLower.includes('validator')) {
        return 'Staking Protocol';
    } else if (bioLower.includes('exchange') || bioLower.includes('dex')) {
        return 'Exchange';
    } else if (bioLower.includes('oracle') || bioLower.includes('data')) {
        return 'Oracle/Data';
    } else {
        return 'Crypto Entity';
    }
}

// Simple markdown parser
function parseMarkdown(markdown) {
    if (!markdown) return '';
    
    return markdown
        // Headers
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // Bold
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        // Lists
        .replace(/^\- (.*$)/gim, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
        // Paragraphs
        .replace(/\n\n/gim, '</p><p>')
        .replace(/^(?!<[h|u|l|a])(.+)$/gim, '<p>$1</p>')
        // Clean up
        .replace(/<p><\/p>/gim, '')
        .replace(/<p>(<h[1-6]>)/gim, '$1')
        .replace(/(<\/h[1-6]>)<\/p>/gim, '$1');
}

// Setup action buttons
function setupActionButtons(character) {
    // GLB button
    if (character.glb) {
        viewGLB.style.display = 'inline-block';
        viewGLB.onclick = () => {
            playSelectSound();
            // Check if file exists, otherwise hide button
            fetch(character.glb, { method: 'HEAD' })
                .then(response => {
                    if (response.ok) {
                        window.open(character.glb, '_blank');
                    } else {
                        alert('3D model file not found');
                    }
                })
                .catch(() => {
                    alert('3D model file not accessible');
                });
        };
    } else {
        viewGLB.style.display = 'none';
    }
    
    // VRM button
    if (character.vrm) {
        viewVRM.style.display = 'inline-block';
        viewVRM.onclick = () => {
            playSelectSound();
            // Check if file exists, otherwise hide button
            fetch(character.vrm, { method: 'HEAD' })
                .then(response => {
                    if (response.ok) {
                        window.open(character.vrm, '_blank');
                    } else {
                        alert('VRM file not found');
                    }
                })
                .catch(() => {
                    alert('VRM file not accessible');
                });
        };
    } else {
        viewVRM.style.display = 'none';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Close modal events
    closeModal.addEventListener('click', closeCharacterModal);
    characterModal.addEventListener('click', (e) => {
        if (e.target === characterModal) {
            closeCharacterModal();
        }
    });
    
    // Keyboard events
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeCharacterModal();
        }
    });
    
    // Music toggle
    musicToggle.addEventListener('click', () => {
        playSelectSound();
        toggleMusic();
    });
    
    // Sound effects toggle
    soundToggle.addEventListener('click', toggleSoundEffects);
    
    // View toggle
    viewToggle.addEventListener('click', () => {
        playSelectSound();
        toggleView();
    });
    
    // Dark mode toggle
    darkModeToggle.addEventListener('click', toggleDarkMode);
    
    // Add hover effects to control buttons
    const controlButtons = document.querySelectorAll('.control-btn');
    controlButtons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            playHoverSound();
        });
    });
    
    // Add hover effects to action buttons
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            playHoverSound();
        });
    });
    
    // Try to setup background music
    setupBackgroundMusic();
}

// Setup sound effects
function setupSoundEffects() {
    // Set volume for sound effects
    if (hoverSound) hoverSound.volume = 0.3;
    if (selectSound) selectSound.volume = 0.5;
    if (closeSound) closeSound.volume = 0.4;
    
    // Handle sound loading errors gracefully
    [hoverSound, selectSound, closeSound].forEach(sound => {
        if (sound) {
            sound.addEventListener('error', () => {
                console.log(`Sound effect failed to load: ${sound.id}`);
            });
        }
    });
}

// Play hover sound effect
function playHoverSound() {
    if (!isSoundEnabled) return;
    
    if (hoverSound && hoverSound.readyState >= 2) {
        hoverSound.currentTime = 0;
        hoverSound.play().catch(e => {
            // Fallback to Web Audio API
            createHoverTone();
        });
    } else {
        createHoverTone();
    }
}

// Play selection sound effect
function playSelectSound() {
    if (!isSoundEnabled) return;
    
    if (selectSound && selectSound.readyState >= 2) {
        selectSound.currentTime = 0;
        selectSound.play().catch(e => {
            // Fallback to Web Audio API
            createSelectTone();
        });
    } else {
        createSelectTone();
    }
}

// Play close sound effect
function playCloseSound() {
    if (!isSoundEnabled) return;
    
    if (closeSound && closeSound.readyState >= 2) {
        closeSound.currentTime = 0;
        closeSound.play().catch(e => {
            // Fallback to Web Audio API
            createCloseTone();
        });
    } else {
        createCloseTone();
    }
}

// Toggle sound effects
function toggleSoundEffects() {
    isSoundEnabled = !isSoundEnabled;
    
    if (isSoundEnabled) {
        soundToggle.textContent = '🔊 SFX';
        playSelectSound(); // Test sound
    } else {
        soundToggle.textContent = '🔇 SFX';
    }
}

// Toggle background music
function toggleMusic() {
    if (isMusicPlaying) {
        bgMusic.pause();
        musicToggle.textContent = '🔇 MUSIC';
        isMusicPlaying = false;
    } else {
        bgMusic.play().catch(e => {
            console.log('Could not play background music:', e);
            // Create a simple audio context for a basic tone
            createSimpleBackgroundTone();
        });
        musicToggle.textContent = '🎵 MUSIC';
        isMusicPlaying = true;
    }
}

// Toggle between normal and compact view
function toggleView() {
    isCompactView = !isCompactView;
    
    if (isCompactView) {
        characterGrid.classList.add('compact');
        viewToggle.textContent = '📱 COMPACT';
    } else {
        characterGrid.classList.remove('compact');
        viewToggle.textContent = '📱 NORMAL';
    }
}

// Toggle dark mode
function toggleDarkMode() {
    isDarkMode = !isDarkMode;
    
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        darkModeToggle.textContent = '🌓 LIGHT MODE';
    } else {
        document.body.classList.remove('dark-mode');
        darkModeToggle.textContent = '🌓 DARK MODE';
    }
}

// Setup background music
function setupBackgroundMusic() {
    // Try to load a simple background track
    bgMusic.volume = 0.3;
    
    // If no audio files work, we'll create a simple tone
    bgMusic.addEventListener('error', () => {
        console.log('Background music failed to load, creating simple tone');
    });
}

// Create hover tone using Web Audio API (fallback)
function createHoverTone() {
    if (!isSoundEnabled) return;
    
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime); // Higher pitch for hover
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.1);
        
    } catch (error) {
        console.log('Could not create hover tone:', error);
    }
}

// Create selection tone using Web Audio API (fallback)
function createSelectTone() {
    if (!isSoundEnabled) return;
    
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(440, audioContext.currentTime); // A4 note
        oscillator.frequency.setValueAtTime(880, audioContext.currentTime + 0.1); // A5 note
        
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.2);
        
    } catch (error) {
        console.log('Could not create selection tone:', error);
    }
}

// Create close tone using Web Audio API (fallback)
function createCloseTone() {
    if (!isSoundEnabled) return;
    
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(660, audioContext.currentTime); // E5 note
        oscillator.frequency.setValueAtTime(330, audioContext.currentTime + 0.1); // E4 note (descending)
        
        gainNode.gain.setValueAtTime(0.15, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.15);
        
    } catch (error) {
        console.log('Could not create close tone:', error);
    }
}

// Create a simple background tone using Web Audio API
function createSimpleBackgroundTone() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(220, audioContext.currentTime); // A3 note
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        
        oscillator.start();
        
        // Stop after 2 seconds
        setTimeout(() => {
            oscillator.stop();
        }, 2000);
        
    } catch (error) {
        console.log('Could not create audio tone:', error);
    }
}

// Update loading progress
function updateLoadingProgress(percentage, message) {
    loadingProgress.style.width = percentage + '%';
    
    // Update loading message if element exists
    const loadingMessage = document.querySelector('.loading-content h2');
    if (loadingMessage && message) {
        loadingMessage.textContent = message;
    }
}

// Hide loading screen
function hideLoadingScreen() {
    setTimeout(() => {
        loadingScreen.classList.add('hidden');
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }, 1000);
}

// Add some fun easter eggs
document.addEventListener('keydown', (e) => {
    // Konami code easter egg
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA'];
    if (!window.konamiProgress) window.konamiProgress = 0;
    
    if (e.code === konamiCode[window.konamiProgress]) {
        window.konamiProgress++;
        if (window.konamiProgress === konamiCode.length) {
            activateEasterEgg();
            window.konamiProgress = 0;
        }
    } else {
        window.konamiProgress = 0;
    }
});

// Easter egg activation
function activateEasterEgg() {
    // Play special sound effect
    playSelectSound();
    
    // Add rainbow effect to all character cards
    const cards = document.querySelectorAll('.character-card');
    cards.forEach(card => {
        card.style.animation = 'borderGlow 0.5s ease-in-out infinite';
        card.style.transform = 'scale(1.1) rotate(5deg)';
    });
    
    // Reset after 3 seconds
    setTimeout(() => {
        cards.forEach(card => {
            card.style.animation = '';
            card.style.transform = '';
        });
    }, 3000);
    
    // Show easter egg message
    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(45deg, #ff00ff, #00ffff);
        color: #000;
        padding: 2rem;
        border-radius: 16px;
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 1.5rem;
        z-index: 10000;
        animation: modalSlideIn 0.3s ease;
    `;
    message.textContent = '🎉 KONAMI CODE ACTIVATED! 🎉';
    document.body.appendChild(message);
    
    setTimeout(() => {
        message.remove();
    }, 3000);
}

// Setup copy and export functionality
function setupCopyAndExport(key, character) {
    console.log('=== SETUP COPY AND EXPORT ===');
    console.log('copyBio button:', copyBio);
    console.log('copyBio ID:', copyBio?.id);
    
    // Setup copy bio functionality
    copyBio.onclick = async () => {
        playSelectSound();
        
        console.log('=== COPY BIO CLICKED ===');
        console.log('This button:', copyBio);
        console.log('Button ID:', copyBio.id);
        console.log('character object:', character);
        console.log('character.bio:', character.bio);
        console.log('character.name:', character.name);
        console.log('key:', key);
        
        let bioText = '';
        
        // Use the original character bio data and clean it up
        if (character.bio) {
            console.log('Using character.bio');
            bioText = character.bio
                // Remove markdown headers
                .replace(/^#+\s*/gm, '')
                // Remove bold and italic formatting
                .replace(/\*\*(.*?)\*\*/g, '$1')
                .replace(/\*(.*?)\*/g, '$1')
                // Convert links to just text
                .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
                // Convert markdown lists to bullet points
                .replace(/^\- /gm, '• ')
                // Clean up extra whitespace
                .replace(/\n\s*\n/g, '\n\n')
                .trim();
        } else {
            console.log('No character.bio, using fallback');
            bioText = `${(character.name || key).replace(/-/g, ' ').replace(/_/g, ' ')}\n\nNo bio available for this character yet.`;
        }
        
        console.log('Final bioText length:', bioText.length);
        console.log('Final bioText:', bioText);
        console.log('=== END COPY BIO ===');
        
        await copyToClipboard(bioText, copyBio);
    };

    // Setup export functionality
    exportJSON.onclick = () => {
        playSelectSound();
        exportCharacterData(key, character);
    };
}

// Copy text to clipboard with visual feedback
async function copyToClipboard(text, button) {
    console.log('=== COPY TO CLIPBOARD ===');
    console.log('Text to copy:', text);
    console.log('Text length:', text.length);
    console.log('Button:', button);
    
    try {
        await navigator.clipboard.writeText(text);
        console.log('Successfully copied to clipboard');
        
        // Visual feedback
        const originalText = button.textContent;
        button.textContent = '✅';
        button.classList.add('copied');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
        
    } catch (err) {
        console.error('Failed to copy text: ', err);
        
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            console.log('Successfully copied using fallback method');
            
            // Visual feedback
            const originalText = button.textContent;
            button.textContent = '✅';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copied');
            }, 2000);
            
        } catch (fallbackErr) {
            console.error('Fallback copy failed: ', fallbackErr);
            
            // Show error feedback
            const originalText = button.textContent;
            button.textContent = '❌';
            
            setTimeout(() => {
                button.textContent = originalText;
            }, 2000);
        }
        
        document.body.removeChild(textArea);
    }
}

// Export character data as JSON file
function exportCharacterData(key, character) {
    // Create comprehensive character data object
    const exportData = {
        id: key,
        name: character.name || key,
        displayName: (character.name || key).replace(/-/g, ' ').replace(/_/g, ' '),
        type: getCharacterType(character.bio),
        bio: character.bio || `# ${character.name || key}\n\nNo bio available for this character yet.`,
        assets: {
            bust_thumbnail: character.bust_thumb,
            bust_image: character.bust_image,
            glb_thumbnail: character.glb_thumb,
            glb_image: character.glb_image,
            glb_model: character.glb,
            vrm_model: character.vrm
        },
        exported_at: new Date().toISOString(),
        exported_from: 'Crypto Avatars Showcase'
    };
    
    // Convert to formatted JSON
    const jsonString = JSON.stringify(exportData, null, 2);
    
    // Create and download file
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${(character.name || key).replace(/[^a-zA-Z0-9]/g, '_')}_character_data.json`;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up the URL object
    URL.revokeObjectURL(url);
    
    // Show success feedback
    const originalText = exportJSON.textContent;
    exportJSON.textContent = '✅ EXPORTED';
    
    setTimeout(() => {
        exportJSON.textContent = originalText;
    }, 2000);
} 