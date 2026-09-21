from server import create_app
from main import info, start, move, end

app = create_app({"info": info, "start": start, "move": move, "end": end})
