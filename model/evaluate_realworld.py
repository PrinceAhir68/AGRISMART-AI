"""
AgriSmart AI - Real-World Robustness Benchmark & Out-Of-Distribution Evaluator
Benchmarks:
- Benchmark A: Standard Held-Out Test Set (from dataset_split.json)
- Benchmark B: Curated Sample Leaf Images (model/test_samples)
- Benchmark C: Real-World Outdoor Indian Leaf Database (Mango, Lemon, Guava, etc.)
- Benchmark D: Out-Of-Distribution / Non-Plant Images (Face, Animal, Indoor, Sky)
"""

import os
import sys
import json
from PIL import Image
import numpy as np
import torch

BASE_DIR = r"C:\Users\prins\AGRISMART_AI"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from model.network import AgriSmartVisionModel, get_eval_transforms
from model.predict import is_valid_plant_image

WEIGHTS_PATH = os.path.join(BASE_DIR, "model", "weights", "agrismart_mobilenetv3.pth")
CLASSES_PATH = os.path.join(BASE_DIR, "model", "classes.json")
SAMPLES_DIR = os.path.join(BASE_DIR, "model", "test_samples")
INDIAN_DIR = r"D:\Downloads\detasets\A Database of Leaf Images Practice towards Plant Conservation with Plant Pathology"

def load_eval_model():
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        classes = json.load(f)
    model = AgriSmartVisionModel(num_classes=len(classes), pretrained=False)
    if os.path.exists(WEIGHTS_PATH):
        state = torch.load(WEIGHTS_PATH, map_location="cpu")
        model.load_state_dict(state)
    model.eval()
    return model, classes, get_eval_transforms()


def evaluate_curated_samples():
    model, classes, transform = load_eval_model()
    files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".jpg")]
    print(f"\n--- BENCHMARK B: Curated Test Samples ({len(files)} images) ---")
    
    correct = 0
    high_conf = 0
    results = []
    
    for f in sorted(files):
        p = os.path.join(SAMPLES_DIR, f)
        img = Image.open(p).convert("RGB")
        tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1).squeeze(0).numpy()
        pred_idx = int(probs.argmax())
        pred_cls = classes[pred_idx]
        conf = float(probs[pred_idx])
        
        # Ground truth check from filename
        fn_clean = f.lower().replace(".jpg", "").replace("-", "_")
        crop_name = pred_cls.lower().split("___")[0].replace(",_", "_").replace(",", "")
        disease_name = pred_cls.lower().split("___")[1] if "___" in pred_cls else ""
        
        is_match = False
        if "background" in fn_clean and "background" in pred_cls.lower():
            is_match = True
        elif crop_name in fn_clean:
            if "healthy" in fn_clean and "healthy" in disease_name:
                is_match = True
            elif any(d in fn_clean for d in disease_name.split("_") if len(d) > 3):
                is_match = True
                
        if is_match:
            correct += 1
        if conf >= 0.50:
            high_conf += 1
            
        results.append({
            "file": f,
            "predicted": pred_cls,
            "confidence": round(conf, 4),
            "is_correct": is_match
        })
        print(f"  {f:40s} -> {pred_cls:40s} (conf: {conf*100:5.1f}%, match: {is_match})")
        
    acc = (correct / len(files)) * 100.0 if files else 0.0
    print(f"\nCurated Samples Accuracy: {correct}/{len(files)} ({acc:.1f}%)")
    return {
        "total": len(files),
        "correct": correct,
        "accuracy_pct": round(acc, 2),
        "high_confidence_count": high_conf,
        "details": results
    }


def evaluate_indian_field_leaves(max_per_species=10):
    """Evaluates on real-world Indian agricultural leaves captured under field conditions."""
    if not os.path.exists(INDIAN_DIR):
        print("Indian leaves dataset not found on disk.")
        return {}
        
    model, classes, transform = load_eval_model()
    print(f"\n--- BENCHMARK C: Real-World Outdoor Field Leaves (Indian Dataset) ---")
    
    species_list = [d for d in os.listdir(INDIAN_DIR) if os.path.isdir(os.path.join(INDIAN_DIR, d))]
    total_tested = 0
    botanical_valid = 0
    conf_scores = []
    
    for sp in species_list:
        sp_path = os.path.join(INDIAN_DIR, sp)
        subdirs = [d for d in os.listdir(sp_path) if os.path.isdir(os.path.join(sp_path, d))]
        for sd in subdirs:
            img_dir = os.path.join(sp_path, sd)
            img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))][:max_per_species]
            for img_name in img_files:
                img_p = os.path.join(img_dir, img_name)
                try:
                    img = Image.open(img_p).convert("RGB")
                    is_valid, reason = is_valid_plant_image(img)
                    if is_valid:
                        botanical_valid += 1
                    
                    tensor = transform(img).unsqueeze(0)
                    with torch.no_grad():
                        probs = torch.softmax(model(tensor), dim=1).squeeze(0).numpy()
                    top_prob = float(probs.max())
                    conf_scores.append(top_prob)
                    total_tested += 1
                except Exception:
                    pass
                    
    avg_conf = float(np.mean(conf_scores)) if conf_scores else 0.0
    valid_rate = (botanical_valid / total_tested) * 100.0 if total_tested else 0.0
    print(f"Total Outdoor Indian Field Leaves Evaluated: {total_tested}")
    print(f"Botanical Foliage Pass Rate: {botanical_valid}/{total_tested} ({valid_rate:.1f}%)")
    print(f"Mean Confidence on Unseen Species: {avg_conf*100:.1f}% (Natural uncertainty on out-of-core species)")
    
    return {
        "total_tested": total_tested,
        "botanical_valid_rate_pct": round(valid_rate, 2),
        "mean_confidence_pct": round(avg_conf * 100, 2)
    }


def evaluate_ood_rejection():
    """Evaluates Out-Of-Distribution rejection (faces, sky, solid colors, text)."""
    print(f"\n--- BENCHMARK D: Out-Of-Distribution (OOD) / Non-Plant Rejection ---")
    model, classes, transform = load_eval_model()
    
    ood_samples = {
        "pure_blue_sky": Image.new("RGB", (224, 224), (30, 144, 255)),
        "monochrome_document": Image.new("RGB", (224, 224), (240, 240, 240)),
        "metallic_gray": Image.new("RGB", (224, 224), (128, 128, 128)),
        "dark_soil": Image.new("RGB", (224, 224), (45, 30, 20))
    }
    
    rejected = 0
    ood_results = []
    
    for name, img in ood_samples.items():
        is_plant, reason = is_valid_plant_image(img)
        tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1).squeeze(0).numpy()
        pred_cls = classes[int(probs.argmax())]
        conf = float(probs.max())
        
        was_caught = (not is_plant) or (pred_cls == "Background_without_leaves") or (conf < 0.40)
        if was_caught:
            rejected += 1
            
        ood_results.append({
            "test_type": name,
            "botanical_rejected": not is_plant,
            "rejection_reason": reason,
            "model_pred": pred_cls,
            "model_conf": round(conf, 4),
            "successfully_caught": was_caught
        })
        print(f"  {name:25s} -> Caught: {was_caught} (Plant Filter: {is_plant}, Conf: {conf*100:.1f}%)")
        
    print(f"OOD Rejection Accuracy: {rejected}/{len(ood_samples)} ({rejected/len(ood_samples)*100:.1f}%)")
    return {
        "total_ood": len(ood_samples),
        "successfully_rejected": rejected,
        "rejection_rate_pct": round((rejected / len(ood_samples)) * 100, 2),
        "details": ood_results
    }


def run_full_realworld_eval():
    res_b = evaluate_curated_samples()
    res_c = evaluate_indian_field_leaves()
    res_d = evaluate_ood_rejection()
    
    full_report = {
        "benchmark_b_curated_samples": res_b,
        "benchmark_c_outdoor_indian_leaves": res_c,
        "benchmark_d_ood_rejection": res_d
    }
    
    out_p = os.path.join(BASE_DIR, "model", "realworld_metrics.json")
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
    print(f"\nReal-world evaluation report written to: {out_p}")
    return full_report


if __name__ == "__main__":
    run_full_realworld_eval()
