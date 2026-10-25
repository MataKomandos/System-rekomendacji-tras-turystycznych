import os
import sys

# Pozwala importować pakiet src z dowolnego katalogu, w którym uruchomiono pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
