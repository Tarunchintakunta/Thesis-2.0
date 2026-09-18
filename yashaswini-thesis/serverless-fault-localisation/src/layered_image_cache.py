# Explores layered image pre-caching and lazy-loading for serverless (Fargate)
# as an advancement over Gupta & Singh (2025).
class LayeredImageCache:
    def __init__(self):
        self.cached_layers = set()

    def pull_image(self, manifest):
        total_time_ms = 0
        for layer in manifest.get("layers", []):
            if layer["digest"] in self.cached_layers:
                # Lazy-loaded/Pre-cached layer takes minimal time
                total_time_ms += 5 
            else:
                # Cold layer pull
                total_time_ms += layer.get("size_mb", 50) * 12 # simulated ping
                self.cached_layers.add(layer["digest"])
                
        return total_time_ms
