import sys
import types
from unittest.mock import MagicMock

import pytest

from scad_export import mesh_repair
from scad_export.exceptions import MeshRepairError


class TestCheckAvailable:
    def test_raises_mesh_repair_error_when_trimesh_missing(self, monkeypatch):
        monkeypatch.setitem(sys.modules, 'trimesh', None)
        with pytest.raises(MeshRepairError):
            mesh_repair.check_available()

    def test_passes_when_trimesh_importable(self, monkeypatch):
        fake_trimesh = types.ModuleType('trimesh')
        monkeypatch.setitem(sys.modules, 'trimesh', fake_trimesh)
        mesh_repair.check_available()


class TestRepairMeshFile:
    def _install_fake_trimesh(self, monkeypatch, load_side_effect=None):
        fake_mesh = MagicMock()
        fake_trimesh = types.ModuleType('trimesh')
        fake_trimesh.load_mesh = MagicMock(side_effect=load_side_effect, return_value=fake_mesh)
        fake_trimesh.repair = MagicMock()
        monkeypatch.setitem(sys.modules, 'trimesh', fake_trimesh)
        return fake_trimesh, fake_mesh

    def test_raises_when_trimesh_not_installed(self, monkeypatch):
        monkeypatch.setitem(sys.modules, 'trimesh', None)
        with pytest.raises(MeshRepairError):
            mesh_repair.repair_mesh_file('part.stl')

    def test_runs_repair_pipeline_and_exports(self, monkeypatch):
        fake_trimesh, fake_mesh = self._install_fake_trimesh(monkeypatch)
        mesh_repair.repair_mesh_file('part.stl')
        fake_trimesh.load_mesh.assert_called_once_with('part.stl')
        fake_trimesh.repair.fix_winding.assert_called_once_with(fake_mesh)
        fake_trimesh.repair.fix_normals.assert_called_once_with(fake_mesh)
        fake_trimesh.repair.fill_holes.assert_called_once_with(fake_mesh)
        fake_mesh.process.assert_called_once_with(validate=True)
        fake_mesh.export.assert_called_once_with('part.stl')

    def test_wraps_load_failure_in_mesh_repair_error(self, monkeypatch):
        self._install_fake_trimesh(monkeypatch, load_side_effect=ValueError('bad file'))
        with pytest.raises(MeshRepairError):
            mesh_repair.repair_mesh_file('part.stl')
