"""
AgriSmart AI Enhancements Tests
"""
import io, json, unittest, numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from model.predict import is_valid_plant_image

client = TestClient(app)

class TestEnhancements(unittest.TestCase):
    def test_non_plant_rejection(self):
        img_blue = Image.fromarray(np.full((100, 100, 3), [10, 30, 240], dtype=np.uint8))
        buf = io.BytesIO()
        img_blue.save(buf, format='JPEG')
        buf.seek(0)
        resp = client.post('/api/predict', files={'file': ('car.jpg', buf, 'image/jpeg')})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['test_detail'] if 'detail' not in data else data['detail'].get('error'), 'NOT_A_PLANT_IMAGE') 

    def test_plant_image_acceptance(self):
        valid, msg = is_valid_plant_image(Image.open('model/test_samples/tomato_early_blight.jpg'))
        self.assertTrue(valid)

    def test_tts_languages(self):
        for l, t in [('hi', 'नमस्ते'), ('gu', 'મमસ્બे'), ('mr', 'नमस्कार'), ('en', 'Hello')]:
            resp = client.get(f'/api/tts?text={t}&lang={l}')
            self.assertEqual(resp.status_code, 200)
            self.assertGreater(len(resp.content), 500)

    def test_marathi_data(self):
        with open('app/data/disease_knowledge.json', 'r', encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual(len(d), 18)
        for k, v in d.items():
            self.assertIn('mr', v['translations'])

if __name__ == '__main__':
    unittest.main()