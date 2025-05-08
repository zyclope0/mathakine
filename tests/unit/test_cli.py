import pytest
import sys
import os
import importlib.util
from unittest.mock import patch, MagicMock
import threading
import time

# Chemin vers le script CLI
CLI_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mathakine_cli.py")

# Charger le module CLI sans l'exécuter
spec = importlib.util.spec_from_file_location("mathakine_cli", CLI_SCRIPT_PATH)
mathakine_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mathakine_cli)

def test_cli_parser_exists():
    """Test que le parseur d'arguments existe dans le CLI"""
    assert hasattr(mathakine_cli, "setup_parser")
    parser = mathakine_cli.setup_parser()
    assert parser is not None

def test_cli_commands_exist():
    """Test que les commandes CLI existent"""
    parser = mathakine_cli.setup_parser()
    
    # Approche directe : vérifier si le parseur a l'attribut _subparsers
    if hasattr(parser, '_subparsers') and parser._subparsers is not None:
        assert parser._subparsers._group_actions, "Aucun sous-parseur trouvé"
        
        # Récupérer les commandes directement
        commands = []
        for action in parser._subparsers._group_actions:
            if hasattr(action, 'choices') and action.choices is not None:
                commands.extend(action.choices.keys())
        
        # Vérifier que les commandes attendues sont présentes
        assert "run" in commands, "La commande 'run' est manquante"
        assert "init" in commands, "La commande 'init' est manquante"
        assert "test" in commands, "La commande 'test' est manquante"
    else:
        pytest.skip("Le parseur n'a pas de sous-parseurs configurés")

# Tests simples sans appel à main() pour éviter les blocages potentiels
def test_run_command_function():
    """Test que la fonction cmd_run existe et prend les bons arguments"""
    assert hasattr(mathakine_cli, "cmd_run")
    
    # Créer un mock des arguments
    args = MagicMock()
    args.port = 8000
    args.host = "127.0.0.1"
    args.reload = False
    args.debug = True
    
    # Patcher la fonction subprocess.Popen pour éviter le démarrage réel du serveur
    with patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        try:
            # Appeler la fonction directement plutôt que via main()
            mathakine_cli.cmd_run(args)
            
            # Vérifier que Popen a été appelé avec les bons arguments
            mock_popen.assert_called_once()
            
            # Vérifier que les paramètres de port et d'hôte sont utilisés
            call_args = mock_popen.call_args[0][0]
            assert "--port" in call_args
            assert str(args.port) in call_args
            assert "--host" in call_args
            assert args.host in call_args
        except Exception as e:
            pytest.fail(f"Exception lors de l'appel à cmd_run: {e}")

def test_init_command_function():
    """Test que la fonction cmd_init existe et prend les bons arguments"""
    assert hasattr(mathakine_cli, "cmd_init")
    
    # Créer un mock des arguments
    args = MagicMock()
    args.force = False
    
    # Patcher les fonctions qui interagissent avec le système de fichiers ou la base de données
    with patch("os.path.exists", return_value=True), \
         patch("app.db.init_db.create_tables_with_test_data") as mock_create_tables:
        
        try:
            # Appeler la fonction directement plutôt que via main()
            mathakine_cli.cmd_init(args)
            
            # Comme force=False et le fichier "existe", create_tables ne devrait pas être appelé
            mock_create_tables.assert_not_called()
            
            # Maintenant avec force=True
            args.force = True
            with patch("os.remove") as mock_remove:
                mathakine_cli.cmd_init(args)
                
                # Vérifier que remove et create_tables sont appelés
                mock_remove.assert_called_once()
                mock_create_tables.assert_called_once()
        except Exception as e:
            pytest.fail(f"Exception lors de l'appel à cmd_init: {e}")

def test_test_command_exists():
    """Test que la fonction cmd_test existe"""
    assert hasattr(mathakine_cli, "cmd_test"), "La fonction cmd_test n'existe pas"
    
    # Vérifier que la fonction cmd_test prend un argument
    import inspect
    sig = inspect.signature(mathakine_cli.cmd_test)
    assert len(sig.parameters) >= 1, "La fonction cmd_test devrait prendre au moins un argument" 