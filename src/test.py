import os
from pathlib import Path

def print_tree(directory, prefix="", ignore_dirs=None, ignore_files=None, max_depth=None, current_depth=0):
    """
    Printa a estrutura de diretórios de forma visual
    
    Args:
        directory: Caminho do diretório
        prefix: Prefixo para indentação
        ignore_dirs: Lista de diretórios a ignorar (ex: ['node_modules', 'venv', '__pycache__'])
        ignore_files: Lista de arquivos a ignorar (ex: ['.DS_Store', '.env'])
        max_depth: Profundidade máxima (None = ilimitado)
        current_depth: Profundidade atual (usado internamente)
    """
    if ignore_dirs is None:
        ignore_dirs = ['node_modules', 'venv', '__pycache__', '.git', 'dist', 'build', '.next', '.vscode', 'env']
    
    if ignore_files is None:
        ignore_files = ['.DS_Store', 'Thumbs.db', '.gitignore']
    
    if max_depth is not None and current_depth >= max_depth:
        return
    
    try:
        directory = Path(directory)
        entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        dirs = [e for e in entries if e.is_dir() and e.name not in ignore_dirs]
        files = [e for e in entries if e.is_file() and e.name not in ignore_files]
        
        # Printar diretórios
        for i, dir_entry in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and len(files) == 0
            connector = "└── " if is_last_dir else "├── "
            print(f"{prefix}{connector}{dir_entry.name}/")
            
            extension = "    " if is_last_dir else "│   "
            print_tree(
                dir_entry, 
                prefix + extension, 
                ignore_dirs, 
                ignore_files,
                max_depth,
                current_depth + 1
            )
        
        # Printar arquivos
        for i, file_entry in enumerate(files):
            is_last = i == len(files) - 1
            connector = "└── " if is_last else "├── "
            
            # Adicionar tamanho do arquivo
            size = file_entry.stat().st_size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f}KB"
            else:
                size_str = f"{size/(1024*1024):.1f}MB"
            
            print(f"{prefix}{connector}{file_entry.name} ({size_str})")
    
    except PermissionError:
        print(f"{prefix}[Acesso negado]")

if __name__ == "__main__":
    import sys
    
    # Pegar diretório do argumento ou usar diretório atual
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"\n📁 Estrutura de: {os.path.abspath(directory)}\n")
    print(os.path.basename(os.path.abspath(directory)) + "/")
    
    print_tree(
        directory,
        prefix="",
        max_depth=5  # Ajuste conforme necessário (None = ilimitado)
    )
    
    print("\n✅ Estrutura gerada com sucesso!\n")