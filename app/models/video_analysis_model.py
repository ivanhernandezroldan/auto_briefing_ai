from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Tuple, Union, Literal

class MusicRecommendation(BaseModel):
    model_config = ConfigDict(extra='allow', populate_by_name=True)
    
    nombre_cancion: str = Field(..., description="Nombre de la canción recomendada")
    artista: str = Field(..., description="Nombre del artista de la canción")

class MusicInfo(BaseModel):
    model_config = ConfigDict(extra='allow', populate_by_name=True)
    
    hay_musica: bool = Field(..., description="Indica si el video debe tener música de fondo")
    recomendacion: Optional[MusicRecommendation] = Field(None, description="Recomendación de música para el video")

class DialogInfo(BaseModel):
    model_config = ConfigDict(extra='allow', populate_by_name=True)
    
    hay_dialogo: bool = Field(..., description="Indica si el video debe tener diálogo")
    dialogo: Optional[List[Tuple[str, str]]] = Field(None, description="Lista de tuplas (hablante, intervención)")

class VideoAnalysis(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "descripcion_original": "Descripción del video original",
                "titulo_portada": "Título para la portada del video",
                "idea_video": "Idea principal del video",
                "gancho_video": "Descripción del gancho inicial (3 primeros segundos)",
                "acciones": ["Acción 1", "Acción 2"],
                "dialogo": {
                    "hay_dialogo": True,
                    "dialogo": [["Hablante", "Texto"]]
                },
                "musica": {
                    "hay_musica": True,
                    "recomendacion": {
                        "nombre_cancion": "Nombre de la canción",
                        "artista": "Nombre del artista"
                    }
                },
                "expectativas_cumplidas": "Explicación de cómo el final cumple las expectativas",
                "caption_video": "Texto para la descripción/caption del video",
                "hashtags": ["hashtag1", "hashtag2"]
            }
        }
    )
    
    descripcion_original: str = Field(..., description="Descripción del video original")
    titulo_portada: str = Field(..., description="Título para la portada del video")
    idea_video: str = Field(..., description="Idea principal del video")
    gancho_video: str = Field(..., description="Descripción del gancho inicial (3 primeros segundos)")
    acciones: List[str] = Field(..., description="Lista de acciones que ocurren en el video")
    dialogo: DialogInfo = Field(..., description="Información sobre el diálogo en el video")
    musica: MusicInfo = Field(..., description="Información sobre la música en el video")
    expectativas_cumplidas: str = Field(..., description="Explicación de cómo el final cumple las expectativas creadas")
    caption_video: str = Field(..., description="Texto para la descripción/caption del video")
    hashtags: Optional[List[str]] = Field(default_factory=list, description="Lista de hashtags para el video") 