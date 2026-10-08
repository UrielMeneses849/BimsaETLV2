import tempfile
import unittest
from io import BytesIO

from openpyxl import load_workbook

from BIMSA_pipeline import process_bimsa


def _record(origin=None, clave="OC000001", precision="Calle"):
    origin_xml = f"<Origen>{origin}</Origen>" if origin is not None else ""
    return f"""
    <datos>
      {origin_xml}
      <Clave_Proyecto>{clave}</Clave_Proyecto>
      <Fecha_Publicacion>01/10/2026</Fecha_Publicacion>
      <Tipo_Proyecto>Proyecto contratado</Tipo_Proyecto>
      <Proyecto>Proyecto de prueba</Proyecto>
      <Region>Centro</Region>
      <proy_ubicacionlatitud>19.432608</proy_ubicacionlatitud>
      <proy_ubicacionlongitud>-99.133209</proy_ubicacionlongitud>
      <Precision>{precision}</Precision>
      <Compania>Compañía de prueba</Compania>
    </datos>
    """


def _workbook_for(*records):
    xml = f"<bobras>{''.join(records)}</bobras>"
    with tempfile.TemporaryDirectory() as output_root:
        _, content = process_bimsa(
            xml,
            "CLASICO",
            output_root=output_root,
            guardar_json=False,
        )
    return load_workbook(BytesIO(content), data_only=True)


class ClassicoSourceSheetsTest(unittest.TestCase):
    def test_mixed_sources_create_two_specialized_sheets(self):
        workbook = _workbook_for(
            _record("Construleads", "OC000001"),
            _record(" Explorer ", "EX000001", "Predio"),
        )

        self.assertEqual(workbook.sheetnames, ["Construleads", "Explorer"])

        construleads = workbook["Construleads"]
        explorer = workbook["Explorer"]
        construleads_headers = [
            construleads.cell(3, column).value
            for column in range(1, construleads.max_column + 1)
        ]
        explorer_headers = [
            explorer.cell(3, column).value
            for column in range(1, explorer.max_column + 1)
        ]

        for header in ("Latitud", "Longitud", "Precisión"):
            self.assertIn(header, construleads_headers)
            self.assertIn(header, explorer_headers)

        self.assertIn("Compania", construleads_headers)
        self.assertNotIn("Compania", explorer_headers)
        self.assertNotIn("Clave Compania", explorer_headers)

        latitude_column = explorer_headers.index("Latitud") + 1
        longitude_column = explorer_headers.index("Longitud") + 1
        precision_column = explorer_headers.index("Precisión") + 1
        self.assertEqual(explorer.cell(4, latitude_column).value, 19.432608)
        self.assertEqual(explorer.cell(4, longitude_column).value, -99.133209)
        self.assertEqual(explorer.cell(4, precision_column).value, "Predio")

        groups = [
            explorer.cell(2, column)
            for column in range(1, explorer.max_column + 1)
            if explorer.cell(2, column).value
        ]
        self.assertEqual(
            [cell.value for cell in groups],
            [
                "Información General",
                "Ubicación del Proyecto",
                "Caracteristicas del Proyecto",
                "Participantes y Contactos",
                "Detalles Adicionales",
            ],
        )
        self.assertTrue(groups[3].fill.fgColor.rgb.endswith("E7E6E6"))
        self.assertTrue(groups[4].fill.fgColor.rgb.endswith("ED7D31"))

    def test_only_explorer_omits_construleads_sheet(self):
        workbook = _workbook_for(_record("Explorer", "EX000001"))
        self.assertEqual(workbook.sheetnames, ["Explorer"])

    def test_only_construleads_omits_explorer_sheet(self):
        workbook = _workbook_for(_record("Construleads", "OC000001"))
        self.assertEqual(workbook.sheetnames, ["Construleads"])

    def test_missing_origin_remains_backward_compatible(self):
        workbook = _workbook_for(_record(None, "OC000001"))
        self.assertEqual(workbook.sheetnames, ["Construleads"])


if __name__ == "__main__":
    unittest.main()
