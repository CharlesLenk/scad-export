import logging

from .exceptions import MeshRepairError

logger = logging.getLogger(__name__)

_INSTALL_MESSAGE = (
    'mesh_repair=True requires the "mesh_repair" optional dependency group. '
    'Install it with: pip install scad_export[mesh_repair]'
)


def _import_trimesh():
    try:
        import trimesh
        return trimesh
    except ImportError as e:
        raise MeshRepairError(_INSTALL_MESSAGE) from e


def check_available():
    """Raise MeshRepairError early if the mesh_repair extra isn't installed."""
    _import_trimesh()


def repair_mesh_file(file_path: str):
    """Run trimesh-based repair on an exported model file, overwriting it in place."""
    trimesh = _import_trimesh()

    try:
        mesh = trimesh.load_mesh(file_path)
        trimesh.repair.fix_winding(mesh)
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.fill_holes(mesh)
        mesh.process(validate=True)
        mesh.export(file_path)
    except Exception as e:
        raise MeshRepairError(f'Failed to repair mesh "{file_path}": {e}') from e

    logger.debug('Repaired mesh: %s', file_path)
