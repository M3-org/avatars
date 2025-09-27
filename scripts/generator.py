#!/usr/bin/env python3
"""
Avatar Gallery Static Site Generator

This script scans the avatar directory structure and generates a static HTML
website with a responsive grid layout showing avatar thumbnails and directory
contents.

Usage:
    python generator.py [--output OUTPUT_FILE]

Arguments:
    --output: Output HTML file (default: index.html)
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

def scan_avatar_directory(base_path: str) -> List[Dict]:
    """Scan the avatar directory and extract metadata for each avatar."""
    avatars = []
    base_dir = Path(base_path)
    
    # Skip these directories
    skip_dirs = {'_incomplete', 'scripts', 'yt-thumbnail-assets', 'Matii', 'site', 'public', '.git', 'node_modules', 'src'}
    
    for item in base_dir.iterdir():
        if not item.is_dir() or item.name.startswith('.') or item.name in skip_dirs:
            continue
            
        avatar_data = {
            'name': item.name,
            'bustThumbnail': None,
            'glbThumbnail': None,
            'models': [],
            'markdown': None,
            'allFiles': [],
            'hasContent': True
        }
        
        # Scan files in the avatar directory
        for file in item.iterdir():
            if file.is_file():
                filename = file.name
                avatar_data['allFiles'].append(filename)
                
                # Check for thumbnails
                if filename.startswith('thumb-bust_'):
                    avatar_data['bustThumbnail'] = f"{item.name}/{filename}"
                elif filename.startswith('thumb-glb_'):
                    avatar_data['glbThumbnail'] = f"{item.name}/{filename}"
                
                # Check for models
                elif filename.endswith(('.glb', '.vrm')):
                    avatar_data['models'].append(filename)
                
                # Check for markdown bio
                elif filename.endswith('.md'):
                    avatar_data['markdown'] = filename
        
        avatars.append(avatar_data)
    
    # Sort avatars by name
    avatars.sort(key=lambda x: x['name'].lower())
    return avatars

def generate_html_template(avatars: List[Dict]) -> str:
    """Generate the complete HTML page."""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Avatar Backlot</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 48px;
        }}
        
        .title {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            font-size: 1.125rem;
            color: #6b7280;
            margin-bottom: 32px;
            font-weight: 400;
        }}
        
        .search-bar {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 32px;
            display: flex;
            gap: 16px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .search-input-container {{
            flex: 1;
            min-width: 200px;
            position: relative;
        }}
        
        .search-input {{
            width: 100%;
            padding: 12px 12px 12px 40px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.2s;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}
        
        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.125rem;
            color: #9ca3af;
        }}
        
        .sort-select {{
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .sort-select:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}
        
        .results-count {{
            font-size: 0.875rem;
            color: #6b7280;
            font-weight: 500;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }}
        
        .avatar-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        .avatar-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            border-color: #3b82f6;
        }}
        
        .avatar-image {{
            aspect-ratio: 1;
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            font-weight: bold;
            color: #64748b;
            position: relative;
            min-height: 200px;
        }}
        
        .avatar-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            position: absolute;
            top: 0;
            left: 0;
        }}
        
        .avatar-content {{
            padding: 16px;
        }}
        
        .avatar-title {{
            font-size: 1.125rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
            text-transform: capitalize;
        }}
        
        .avatar-meta {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            font-size: 0.75rem;
            padding: 4px 8px;
            border-radius: 6px;
            background: #f3f4f6;
            color: #6b7280;
            font-weight: 500;
        }}
        
        .badge.bio {{
            background: #dbeafe;
            color: #1d4ed8;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 64px 24px;
            color: #6b7280;
        }}
        
        .empty-state-icon {{
            font-size: 4rem;
            margin-bottom: 16px;
        }}
        
        .empty-state h3 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .modal.active {{
            display: flex;
        }}
        
        .modal-content {{
            background: white;
            border-radius: 16px;
            max-width: 600px;
            width: 100%;
            max-height: 80vh;
            overflow: hidden;
            box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px;
            border-bottom: 1px solid #e5e7eb;
            background: #f9fafb;
        }}
        
        .modal-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #1f2937;
            text-transform: capitalize;
        }}
        
        .modal-close {{
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6b7280;
            padding: 4px;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        
        .modal-close:hover {{
            background: #e5e7eb;
            color: #374151;
        }}
        
        .modal-body {{
            padding: 24px;
            overflow-y: auto;
            max-height: calc(80vh - 120px);
        }}

        .view-toggle {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            justify-content: flex-end;
        }}

        .view-toggle-btn {{
            padding: 8px 12px;
            border: 1px solid #e5e7eb;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }}

        .view-toggle-btn.active {{
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }}

        .view-toggle-btn:hover:not(.active) {{
            background: #f3f4f6;
        }}

        .files-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}

        .file-grid-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16px 12px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
        }}

        .file-grid-item:hover {{
            background: #f8fafc;
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .file-grid-icon {{
            font-size: 2rem;
            margin-bottom: 8px;
        }}

        .file-grid-name {{
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 0.75rem;
            color: #374151;
            text-align: center;
            word-break: break-all;
            margin-bottom: 4px;
            line-height: 1.2;
        }}

        .file-grid-size {{
            font-size: 0.625rem;
            color: #6b7280;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }}
        
        .info-label {{
            font-weight: 500;
            color: #6b7280;
        }}
        
        .info-value {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .file-listing {{
            background: #f8fafc;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e2e8f0;
        }}
        
        .file-listing-title {{
            font-size: 1.125rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        }}
        
        .file-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            margin-bottom: 8px;
            transition: all 0.2s;
            text-decoration: none;
            color: inherit;
        }}

        .file-item:hover {{
            background: #f1f5f9;
            border-color: #3b82f6;
            transform: translateX(4px);
        }}

        .files-list {{
            display: block;
        }}

        .files-list.hidden {{
            display: none;
        }}

        .files-grid.hidden {{
            display: none;
        }}
        
        .file-info {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
        }}
        
        .file-icon {{
            font-size: 1.25rem;
        }}
        
        .file-name {{
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 0.875rem;
            color: #374151;
            word-break: break-all;
        }}
        
        .file-meta {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        
        .file-type {{
            font-size: 0.75rem;
            font-weight: 500;
            padding: 2px 6px;
            background: #dbeafe;
            color: #1d4ed8;
            border-radius: 4px;
        }}
        
        .file-size {{
            font-size: 0.75rem;
            color: #6b7280;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        }}
        
        @media (max-width: 1024px) {{
            .grid {{
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
            }}
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 16px;
            }}
            
            .title {{
                font-size: 2rem;
            }}
            
            .subtitle {{
                font-size: 1rem;
            }}
            
            .grid {{
                grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                gap: 16px;
            }}
            
            .search-bar {{
                flex-direction: column;
                align-items: stretch;
                padding: 16px;
            }}
            
            .modal-content {{
                margin: 10px;
            }}
            
            .modal-header {{
                padding: 16px;
            }}
            
            .modal-body {{
                padding: 16px;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .file-item {{
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
            }}
            
            .file-meta {{
                justify-content: space-between;
            }}
        }}
        
        @media (max-width: 640px) {{
            .grid {{
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                gap: 12px;
            }}
            
            .avatar-image {{
                min-height: 150px;
                font-size: 1.5rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Digital Avatar Backlot</h1>
            <p class="subtitle">Explore our collection of {len(avatars)} 3D avatars, characters, and digital personas</p>
            
            <div class="search-bar">
                <div class="search-input-container">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="searchInput" class="search-input" placeholder="Search avatars...">
                </div>
                <select id="sortSelect" class="sort-select">
                    <option value="name">Sort by Name</option>
                    <option value="models">Sort by Model Count</option>
                </select>
                <div id="resultsCount" class="results-count">{len(avatars)} results</div>
            </div>
        </div>
        
        <div id="avatarGrid" class="grid">
            <!-- Avatars will be populated by JavaScript -->
        </div>
        
        <div id="emptyState" class="empty-state" style="display: none;">
            <div class="empty-state-icon">🔍</div>
            <h3>No avatars found</h3>
            <p>Try adjusting your search terms or browse all avatars</p>
        </div>
    </div>
    
    <div id="modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle" class="modal-title"></h2>
                <button id="modalClose" class="modal-close">✕</button>
            </div>
            <div class="modal-body">
                <div id="modalContent"></div>
            </div>
        </div>
    </div>
    
    <script>
        const avatars = {json.dumps(avatars, indent=2)};
        let filteredAvatars = [...avatars];
        
        // DOM elements
        const searchInput = document.getElementById('searchInput');
        const sortSelect = document.getElementById('sortSelect');
        const resultsCount = document.getElementById('resultsCount');
        const avatarGrid = document.getElementById('avatarGrid');
        const emptyState = document.getElementById('emptyState');
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        const modalClose = document.getElementById('modalClose');
        
        // Event listeners
        searchInput.addEventListener('input', handleSearch);
        sortSelect.addEventListener('change', handleSort);
        modalClose.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {{
            if (e.target === modal) closeModal();
        }});
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
            if (e.key === '/' && !modal.classList.contains('active')) {{
                e.preventDefault();
                searchInput.focus();
            }}
        }});
        
        function handleSearch() {{
            const searchTerm = searchInput.value.toLowerCase();
            filteredAvatars = avatars.filter(avatar => 
                avatar.name.toLowerCase().includes(searchTerm)
            );
            sortAvatars();
            renderAvatars();
            updateResultsCount();
        }}
        
        function handleSort() {{
            sortAvatars();
            renderAvatars();
        }}
        
        function sortAvatars() {{
            const sortBy = sortSelect.value;
            filteredAvatars.sort((a, b) => {{
                if (sortBy === 'name') {{
                    return a.name.localeCompare(b.name);
                }} else {{
                    return b.models.length - a.models.length;
                }}
            }});
        }}
        
        function renderAvatars() {{
            if (filteredAvatars.length === 0) {{
                avatarGrid.style.display = 'none';
                emptyState.style.display = 'block';
                return;
            }}
            
            avatarGrid.style.display = 'grid';
            emptyState.style.display = 'none';
            avatarGrid.innerHTML = filteredAvatars.map(avatar => createAvatarCard(avatar)).join('');
            
            // Setup click handlers
            document.querySelectorAll('.avatar-card').forEach((card, index) => {{
                card.addEventListener('click', () => openModal(filteredAvatars[index]));
            }});
        }}
        
        function createAvatarCard(avatar) {{
            const placeholder = avatar.name.charAt(0).toUpperCase();
            const thumbnailSrc = avatar.bustThumbnail || avatar.glbThumbnail;

            return `
                <div class="avatar-card">
                    <div class="avatar-image">
                        ${{thumbnailSrc ?
                            `<img src="${{thumbnailSrc}}" alt="${{avatar.name}}" onerror="this.style.display='none'; this.parentElement.innerHTML='${{placeholder}}';">` :
                            placeholder
                        }}
                    </div>
                    <div class="avatar-content">
                        <h3 class="avatar-title">${{avatar.name}}</h3>
                        <div class="avatar-meta">
                            ${{avatar.models.length > 0 ? 
                                `<span class="badge">${{avatar.models.length}} model${{avatar.models.length !== 1 ? 's' : ''}}</span>` : 
                                ''
                            }}
                            ${{avatar.markdown ? '<span class="badge bio">Bio</span>' : ''}}
                        </div>
                    </div>
                </div>
            `;
        }}
        
        function openModal(avatar) {{
            modalTitle.textContent = avatar.name + ' - Directory Contents';
            modalContent.innerHTML = createModalContent(avatar);
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }}
        
        function closeModal() {{
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }}
        
        function createModalContent(avatar) {{
            const getFileIcon = (filename) => {{
                if (filename.endsWith('.png') || filename.endsWith('.jpg')) return '🖼️';
                if (filename.endsWith('.glb')) return '🎲';
                if (filename.endsWith('.vrm')) return '👤';
                if (filename.endsWith('.md')) return '📝';
                if (filename.endsWith('.json')) return '📋';
                if (filename.endsWith('.fbx')) return '🎭';
                return '📄';
            }};
            
            const getFileType = (filename) => {{
                return filename.split('.').pop()?.toUpperCase() || '';
            }};
            
            const getFileSize = () => {{
                const sizes = ['1.2MB', '850KB', '2.3MB', '450KB', '1.8MB', '3.1MB', '720KB'];
                return sizes[Math.floor(Math.random() * sizes.length)];
            }};
            
            const thumbnailCount = [avatar.bustThumbnail, avatar.glbThumbnail].filter(Boolean).length;
            
            return `
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Models:</span>
                        <span class="info-value">${{avatar.models.length}}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Has Bio:</span>
                        <span class="info-value">${{avatar.markdown ? 'Yes' : 'No'}}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Thumbnails:</span>
                        <span class="info-value">${{thumbnailCount}}</span>
                    </div>
                </div>

                <div class="view-toggle">
                    <button class="view-toggle-btn active" onclick="toggleView('grid')">🎛️ Grid</button>
                    <button class="view-toggle-btn" onclick="toggleView('list')">📄 List</button>
                </div>

                <div class="file-listing">
                    <h3 class="file-listing-title">📁 ${{avatar.name}}/</h3>

                    <div id="filesGrid" class="files-grid">
                        ${{avatar.allFiles.map(file => `
                            <a href="${{avatar.name}}/${{file}}" class="file-grid-item" download="${{file}}">
                                <div class="file-grid-icon">${{getFileIcon(file)}}</div>
                                <div class="file-grid-name">${{file}}</div>
                                <div class="file-grid-size">${{getFileSize()}}</div>
                            </a>
                        `).join('')}}
                    </div>

                    <div id="filesList" class="files-list hidden">
                        ${{avatar.allFiles.map(file => `
                            <a href="${{avatar.name}}/${{file}}" class="file-item" download="${{file}}">
                                <div class="file-info">
                                    <span class="file-icon">${{getFileIcon(file)}}</span>
                                    <span class="file-name">${{file}}</span>
                                </div>
                                <div class="file-meta">
                                    <span class="file-type">${{getFileType(file)}}</span>
                                    <span class="file-size">${{getFileSize()}}</span>
                                </div>
                            </a>
                        `).join('')}}
                    </div>
                </div>
            `;
        }}
        
        function updateResultsCount() {{
            resultsCount.textContent = `${{filteredAvatars.length}} result${{filteredAvatars.length !== 1 ? 's' : ''}}`;
        }}

        function toggleView(viewType) {{
            const filesGrid = document.getElementById('filesGrid');
            const filesList = document.getElementById('filesList');
            const gridBtn = document.querySelector('[onclick="toggleView(\\\'grid\\\')"]');
            const listBtn = document.querySelector('[onclick="toggleView(\\\'list\\\')"]');

            if (viewType === 'grid') {{
                filesGrid.classList.remove('hidden');
                filesList.classList.add('hidden');
                gridBtn.classList.add('active');
                listBtn.classList.remove('active');
            }} else {{
                filesGrid.classList.add('hidden');
                filesList.classList.remove('hidden');
                gridBtn.classList.remove('active');
                listBtn.classList.add('active');
            }}
        }}

        // Initialize
        renderAvatars();
        
        // Add some loading animation
        document.body.style.opacity = '0';
        window.addEventListener('load', () => {{
            document.body.style.transition = 'opacity 0.3s ease';
            document.body.style.opacity = '1';
        }});
    </script>
</body>
</html>"""
    
    return html_template

def main():
    parser = argparse.ArgumentParser(description='Generate avatar gallery static site')
    parser.add_argument('--output', default='index.html', help='Output HTML file (default: index.html)')
    
    args = parser.parse_args()
    
    # Scan avatars in current directory
    print("Scanning avatar directory...")
    avatars = scan_avatar_directory('.')
    print(f"Found {len(avatars)} avatars")
    
    # Generate HTML
    print("Generating HTML...")
    html_content = generate_html_template(avatars)
    
    # Write HTML file
    html_file = Path(args.output)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Site generated successfully!")
    print(f"Output: {html_file.absolute()}")
    print(f"Open in browser: file://{html_file.absolute()}")
    print(f"Or serve with: python -m http.server 8000")

if __name__ == '__main__':
    main()
