from typing import List
from pydantic import BaseModel


class Point(BaseModel):
    x: float
    y: float


class BoundingBox(BaseModel):
    topLeft: Point
    topRight: Point
    bottomRight: Point
    bottomLeft: Point


class Result(BaseModel):
    boundingBox: BoundingBox
    detectionScore: float
    embeddings: List[float]


class BaseResponse(BaseModel):
    requestId: str
    algorithmName: str
    algorithmVersion: str


class AlgorithmResponse(BaseResponse):
    results: List[Result]


class LouvRequest(AlgorithmResponse):
    collection: str
