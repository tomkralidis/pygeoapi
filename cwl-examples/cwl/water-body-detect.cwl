cwlVersion: v1.0

class: CommandLineTool
id: detect-water-body
requirements:
    EnvVarRequirement:
      envDef:
        PYTHONPATH: /app
    ResourceRequirement:
      coresMax: 1
      ramMax: 512
    DockerRequirement:
      dockerPull: water-body-detection:local
baseCommand: ["python", "-m", "app"]
arguments: []
inputs:
  item:
    type: string
    inputBinding:
        prefix: --input-item
  aoi:
    type: string
    inputBinding:
        prefix: --aoi
  epsg:
    type: string
    inputBinding:
        prefix: --epsg
  band:
    type:
      - type: array
        items: string
        inputBinding:
          prefix: '--band'

outputs:
  water-body:
    outputBinding:
        glob: .
    type: Directory

