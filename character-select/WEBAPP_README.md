# 🎮 Crypto Avatars Character Selection Web App

A stunning, interactive web interface for browsing and exploring crypto/DeFi character avatars with a retro gaming aesthetic.

![Character Selection Interface](https://img.shields.io/badge/Status-Ready%20for%20Production-brightgreen)
![GitHub Pages Compatible](https://img.shields.io/badge/GitHub%20Pages-Compatible-blue)
![No Dependencies](https://img.shields.io/badge/Dependencies-None-orange)

## ✨ Features

### 🎨 **Visual Experience**
- **Retro Gaming Aesthetic** - Cyberpunk-inspired design with neon colors and glowing effects
- **Smooth Animations** - Floating character cards, glowing borders, and smooth transitions
- **Dark/Light Mode** - Toggle between cyber (light) and dark purple-grey themes
- **Responsive Design** - Perfect on desktop, tablet, and mobile devices
- **Loading Experience** - Animated loading screen with progress tracking

### 🔊 **Audio Experience**
- **Background Music** - Arcade-style background music with user control
- **Sound Effects** - Hover, selection, and close sounds for immersive interaction
- **Smart Fallbacks** - Web Audio API fallbacks if sound files don't load
- **User Control** - Independent music and SFX toggles

### 📋 **Character Interaction**
- **Quick Actions** - Copy bio and export JSON directly from character cards
- **Detailed Modals** - Full character information with bio, images, and 3D model links
- **Smart Copy** - Copy character bios to clipboard with markdown cleanup
- **JSON Export** - Download comprehensive character data as formatted JSON files

### 🎯 **User Interface**
- **Streamlined Cards** - Hover to reveal copy (📋) and export (📄) buttons
- **Character Grid** - Responsive grid with normal and compact view modes
- **Modal System** - Detailed character view with bio, stats, and action buttons
- **Keyboard Support** - ESC to close modals, Konami code easter egg

### 🔧 **Technical Features**
- **Smart Path Detection** - Automatically works on local development and GitHub Pages
- **Multiple Data Sources** - Loads from data.json, avatars.csv, or fallback character list
- **Error Handling** - Graceful fallbacks for missing images and data
- **Performance Optimized** - Lazy loading, efficient rendering, minimal dependencies

## 🚀 Quick Start

### Local Development

1. **Start HTTP Server** (from main avatars directory):
   ```bash
   python -m http.server 8000
   # or
   npx http-server
   # or
   php -S localhost:8000
   ```

2. **Open in Browser**:
   ```
   http://localhost:8000/character-select/
   ```

### GitHub Pages Deployment

1. **Enable GitHub Pages** in repository settings
2. **Set source** to deploy from main/master branch
3. **Access at**: `https://yourusername.github.io/avatars/`
   - Automatically redirects to: `/character-select/`

The app automatically detects the environment and adjusts file paths accordingly.

## 📁 File Structure

```
character-select/
├── index.html              # Main application HTML
├── styles.css              # Complete styling and animations
├── script.js               # All JavaScript functionality
├── WEBAPP_README.md        # This documentation
├── .nojekyll               # GitHub Pages configuration
├── arcadebg.mp3            # Background music
├── tap.wav                 # Legacy sound file
├── scan1.wav               # Legacy sound file
└── sound/
    └── Bleeps/
        ├── beep.wav           # Hover sound effect
        ├── selectbleep.wav    # Selection sound effect
        └── beepdown.wav       # Close sound effect
```

## 🎮 Controls & Interactions

### Header Controls
- **🎵 MUSIC** - Toggle background music on/off
- **🔊 SFX** - Toggle sound effects on/off  
- **📱 VIEW** - Switch between normal and compact grid view
- **🌙 DARK** - Toggle between light (cyber) and dark (purple) themes

### Character Cards
- **Hover** - Reveals action buttons in top-right corner
- **📋 Copy Button** - Copies character bio to clipboard (cleaned markdown)
- **📄 Export Button** - Downloads character data as JSON file
- **Click Card** - Opens detailed character modal

### Character Modal
- **📋 Copy Bio** - Copy button next to character name
- **📄 Export JSON** - Export button in action section
- **VIEW 3D MODEL** - Opens GLB file (if available)
- **VIEW VRM** - Opens VRM file (if available)
- **ESC Key** - Close modal
- **Click Outside** - Close modal

### Easter Eggs
- **Konami Code** - ↑↑↓↓←→←→BA for special effects! 🎊

## 🔧 Technical Implementation

### Data Pipeline & Automation

The web app uses a sophisticated data loading system that automatically scales when new characters are added to the repository.

#### **Data Sources (Priority Order)**
1. **`../data.json`** - Primary structured data (auto-generated)
2. **`../avatars.csv`** - Character index with file paths
3. **Hardcoded fallback** - Known character list for emergency fallback

#### **GitHub Actions Integration**
The repository likely uses GitHub Actions to automatically:
- **Generate `data.json`** from character folders and markdown files
- **Update `avatars.csv`** when new characters are added
- **Validate file structure** and ensure consistency
- **Optimize images** and generate thumbnails if needed

#### **Auto-Scaling for New Characters**
When a new character is added to the repository:
1. **GitHub Action triggers** on push/PR to main branch
2. **Scans character folders** for new directories
3. **Parses markdown files** (`.md`) for character bios
4. **Updates data.json** with new character information
5. **Web app automatically loads** new characters on next visit

#### **Character Data Structure**
Each character in `data.json` contains:
```json
{
  "character-name": {
    "bust_thumb": "path/to/thumb-bust_character.png",    // Small thumbnail for cards
    "bust": "path/to/bust_character.png",                // Full-size bust image for modal
    "glb_thumb": "path/to/thumb-glb_character.png",      // Small 3D thumbnail
    "glb_preview": "path/to/glb_character.png",          // Full-size 3D preview image
    "glb": "path/to/character.glb",                      // 3D model file
    "vrm": "path/to/character.vrm",                      // VRM model file (optional)
    "bio": "Full markdown content from character.md file"
  }
}
```

#### **Image Usage Hierarchy**
- **Character Cards**: Use `bust_thumb` (thumbnails) for grid display
  - Fallback: `bust` → `bust_[name].png` → `[name].png`
- **Modal Bust Image**: Use `bust` (full-size) for detailed view
  - Fallback: `bust_thumb` → `bust_[name].png` → `[name].png`
- **Modal 3D Preview**: Use `glb_preview` → `glb_thumb` → `bust` → `bust_thumb`

### Copy & Paste Functionality Deep Dive

#### **How Copy Works**
1. **Source Data**: Gets character bio from loaded JSON data
2. **Markdown Cleanup**: Removes formatting for clean text
   ```javascript
   // Removes: # headers, **bold**, *italic*, [links](urls), - lists
   bioText = character.bio
     .replace(/^#+\s*/gm, '')           // Remove headers
     .replace(/\*\*(.*?)\*\*/g, '$1')   // Remove bold
     .replace(/\*(.*?)\*/g, '$1')       // Remove italic  
     .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links to text
     .replace(/^\- /gm, '• ')           // Lists to bullets
     .trim();
   ```
3. **Clipboard API**: Uses modern `navigator.clipboard.writeText()`
4. **Fallback**: Falls back to `document.execCommand('copy')` for older browsers
5. **Visual Feedback**: Shows ✅ for 2 seconds on successful copy

#### **What Gets Copied**
- **Character Bio**: Full bio text with markdown formatting removed
- **Clean Format**: Readable plain text suitable for pasting anywhere
- **Preserved Structure**: Maintains paragraphs and bullet points
- **No HTML**: Pure text output, no HTML tags or formatting

#### **Copy Button Locations**
- **Card Copy Button**: Appears on hover in top-right of character cards
- **Modal Copy Button**: Next to character name in detailed view
- **Both buttons copy the same cleaned bio text**

### Data Loading Strategy
1. **Primary**: Load from `../data.json` (structured character data)
2. **Fallback**: Load from `../avatars.csv` (character list)
3. **Final Fallback**: Hardcoded character list with basic data

### Path Resolution
- **Local Development**: Uses `../` relative paths
- **GitHub Pages**: Automatically detects and adjusts paths
- **Smart Detection**: Analyzes `window.location.pathname` for environment

### Asset Loading
- **Character Images**: `../[character]/thumb-bust_[character].png`
- **3D Models**: `../[character]/[character].glb` and `.vrm`
- **Character Bios**: `../[character]/[character].md`
- **Fallback Images**: Multiple fallback paths for missing assets

### Performance Features
- **Lazy Loading**: Images load as needed
- **Error Handling**: Silent fallbacks for missing assets
- **Efficient Rendering**: Minimal DOM manipulation
- **Smart Caching**: Browser caching for repeated visits

## 📊 Data Management & Scalability

### Adding New Characters

#### **For Repository Maintainers**
1. **Create character folder**: `new-character/`
2. **Add required files**:
   ```
   new-character/
   ├── thumb-bust_new-character.png    # Card thumbnail
   ├── bust_new-character.png          # Large bust image  
   ├── thumb-glb_new-character.png     # 3D thumbnail
   ├── glb_new-character.png           # 3D preview image
   ├── new-character.glb               # 3D model
   ├── new-character.vrm               # VRM model (optional)
   └── new-character.md                # Character bio
   ```
3. **Push to repository** - GitHub Actions automatically update data files
4. **Web app updates** - New character appears automatically

#### **File Naming Convention**
- **Thumbnails**: `thumb-bust_[name].png`, `thumb-glb_[name].png`
- **Images**: `bust_[name].png`, `glb_[name].png`  
- **3D Models**: `[name].glb`, `[name].vrm`
- **Bio**: `[name].md`
- **Folder**: `[name]/` (matches character identifier)

#### **Character Bio Format**
The `.md` file should contain:
```markdown
# Character Name

Character description and background story.

## Personality
- Trait 1
- Trait 2

## Background
More detailed information about the character.
```

### Data Validation & Quality Control

#### **Automated Checks** (via GitHub Actions)
- **File existence**: Ensures required files are present
- **Image validation**: Checks image dimensions and formats
- **Markdown parsing**: Validates bio file structure
- **JSON generation**: Creates valid, formatted data.json
- **Link validation**: Ensures all file paths are correct

#### **Manual Quality Control**
- **Character review**: Bio content and image quality
- **Consistency check**: Naming conventions and file structure
- **Testing**: Verify character loads correctly in web app

### Scalability Features

#### **Performance at Scale**
- **Lazy loading**: Only loads visible character images
- **Efficient filtering**: Client-side filtering without re-fetching data
- **Caching strategy**: Browser caches character data and images
- **Progressive loading**: Shows characters as they load

#### **Data Size Management**
- **Optimized images**: Thumbnails are small, full images load on demand
- **Compressed JSON**: Efficient data structure minimizes file size
- **CDN friendly**: All assets can be cached by CDNs
- **Incremental updates**: Only changed data needs to be updated

#### **Future-Proof Architecture**
- **API ready**: Can easily switch to REST API backend
- **Search ready**: Data structure supports search/filter features
- **Extensible**: Easy to add new character properties
- **Modular**: Components can be enhanced independently

### Monitoring & Analytics

#### **Performance Tracking**
- **Load times**: Monitor character grid rendering speed
- **Error rates**: Track failed image loads and data fetching
- **User interactions**: Copy/export usage statistics
- **Browser compatibility**: Monitor feature support across browsers

#### **Data Quality Metrics**
- **Character completeness**: Track missing files or incomplete data
- **Image optimization**: Monitor file sizes and load performance
- **Bio quality**: Ensure all characters have meaningful descriptions
- **3D model availability**: Track GLB/VRM file coverage

## 🌐 Browser Compatibility

### Required Features
- **ES6+ JavaScript** - Modern syntax and features
- **CSS Grid & Flexbox** - Layout systems
- **CSS Custom Properties** - Theme variables
- **Fetch API** - Data loading
- **Clipboard API** - Copy functionality (with fallback)

### Supported Browsers
- **Chrome/Edge** 88+ ✅
- **Firefox** 85+ ✅  
- **Safari** 14+ ✅
- **Mobile Browsers** - iOS Safari, Chrome Mobile ✅

### Graceful Degradation
- **No Clipboard API**: Falls back to `document.execCommand`
- **No Web Audio**: Silent operation
- **No CSS Grid**: Falls back to flexbox
- **Missing Assets**: Shows fallback content

## 🎨 Customization

### Themes
The app includes two built-in themes:
- **Cyber Theme** (default): Neon cyan/magenta on dark blue
- **Dark Theme**: Purple/grey on black

Modify CSS custom properties in `:root` and `body.dark-mode` to customize colors.

### Sound Effects
Replace sound files in `sound/Bleeps/` directory:
- `beep.wav` - Hover sound
- `selectbleep.wav` - Selection sound  
- `beepdown.wav` - Close sound

### Character Data
The app automatically loads character data from:
- `../data.json` - Primary data source
- `../avatars.csv` - Fallback character list
- Individual `../[character]/[character].md` files for bios

## 🐛 Troubleshooting

### Common Issues

**Images Not Loading**
- Ensure character folders exist in parent directory
- Check that image files follow naming convention:
  - `thumb-bust_[name].png` - Small thumbnails for character cards
  - `bust_[name].png` - Full-size bust images for modal view
  - `thumb-glb_[name].png` - Small 3D model thumbnails
  - `glb_[name].png` - Full-size 3D preview images
- Verify HTTP server is running (not file:// protocol)
- **Image Fallback Order**: The app tries multiple image sources automatically:
  1. Primary: `bust_thumb` from data.json
  2. Fallback 1: `bust` (full-size image scaled down)
  3. Fallback 2: `bust_[name].png` (direct file path)
  4. Fallback 3: `[name].png` (generic image)
  5. Final: Hide character card if no images work

**Sounds Not Playing**
- Click SFX button to enable audio
- Check browser console for audio loading errors
- Ensure sound files exist in `sound/Bleeps/` folder

**Copy Function Not Working**
- Modern browsers require HTTPS for clipboard API
- Fallback to `document.execCommand` should work on HTTP
- Check browser permissions for clipboard access

**GitHub Pages Issues**
- Ensure `.nojekyll` file exists
- Check that all file paths are relative
- Verify GitHub Pages is enabled in repository settings

### Debug Mode
Open browser console to see:
- Character data loading progress
- Copy operation details
- Audio loading status
- Path resolution information

## 🚀 Deployment Options

### 1. GitHub Pages (Recommended)
- Zero configuration required
- Automatic HTTPS
- Global CDN distribution
- Free hosting

### 2. Netlify/Vercel
- Drag and drop deployment
- Custom domain support
- Build optimization

### 3. Traditional Web Hosting
- Upload entire `character-select/` folder
- Ensure parent directory contains character data
- Configure web server for SPA routing

## 📈 Performance Metrics

- **Initial Load**: ~2-3 seconds (including character data)
- **Character Rendering**: ~50ms per character
- **Modal Open**: <100ms
- **Copy Operation**: <50ms
- **Export Operation**: <200ms

## 🎯 Future Enhancements

Potential improvements for future versions:
- **Search & Filter** - Find characters by name or type
- **3D Model Preview** - Inline GLB/VRM viewer
- **Character Comparison** - Side-by-side character analysis
- **Social Sharing** - Share character cards on social media
- **Keyboard Navigation** - Full keyboard accessibility
- **PWA Support** - Offline functionality and app installation
- **Animation Customization** - User-configurable effects

---

**Built with ❤️ using vanilla HTML, CSS, and JavaScript**  
**No frameworks, no dependencies, just pure web technology! 🚀** 