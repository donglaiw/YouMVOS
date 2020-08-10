template_proofread_seg = """{
  "Comment": "%s",
  "ServerType": "imagetiles",

  "SourceFileNameTemplate": "%s",
  "SourceParamSequence": "s",
  "SourceMinS": 0,
  "SourceMaxS": %d,
  "SourceMinR": 1,
  "SourceMaxR": 1,
  "SourceMinC": 1,
  "SourceMaxC": 1,

  "MipMapFileNameTemplate": "%s",
  "MipMapParamSequence": "s",
  "SourceMinM": 0,
  "SourceMaxM": 0,
  "SourceTileSizeX": %d,
  "SourceTileSizeY": %d,
  "SourceBytesPerPixel": 3,
  "MissingImagePolicy": "nearest",
  "SourceSectionOrder": "%s",

  "TargetDataSizeX": %d,
  "TargetDataSizeY": %d,
  "TargetDataSizeZ": %d,
  "OffsetX": 0,
  "OffsetY": 0,
  "OffsetZ": 0,
  "OffsetMip": 0,
  "TargetVoxelSizeXnm": 4.000000,
  "TargetVoxelSizeYnm": 4.000000,
  "TargetVoxelSizeZnm": 4.000000,
  "TargetLayerName": "%s"
  }
"""
