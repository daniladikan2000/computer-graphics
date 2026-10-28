import io
import base64
from typing import Dict, Any, Tuple
from PIL import Image


def load_image(file_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(file_bytes)).convert("RGB")


def to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def to_grayscale(img: Image.Image) -> Image.Image:
    if img.mode == "L":
        return img
    return img.convert("L")


def get_stats(gray_img: Image.Image) -> Dict[str, Any]:
    pixels = list(gray_img.getdata())
    return {
        "min": min(pixels) if pixels else 0,
        "max": max(pixels) if pixels else 0
    }


def linear_stretch(gray: Image.Image, robust: bool = False) -> Tuple[Image.Image, str]:
    hist = gray.histogram()
    total = sum(hist)

    if robust:
        low_limit = total * 0.01
        high_limit = total * 0.99
        accum = 0
        i_min, i_max = 0, 255
        for i, count in enumerate(hist):
            accum += count
            if accum >= low_limit:
                i_min = i
                break
        accum = 0
        for i, count in enumerate(hist):
            accum += count
            if accum >= high_limit:
                i_max = i
                break
    else:
        pixels = list(gray.getdata())
        i_min = min(pixels)
        i_max = max(pixels)

    if i_max <= i_min:
        return gray, f"I_min={i_min}, I_max={i_max}"

    scale = 255.0 / (i_max - i_min)
    lut = [min(255, max(0, int(round((i - i_min) * scale)))) for i in range(256)]
    res = gray.point(lut)
    name = "Робастное" if robust else "Линейное"
    return res, f"{name}: [{i_min}, {i_max}] → [0, 255]"


def otsu_threshold(hist: list) -> int:
    total = sum(hist)
    total_sum = sum(i * count for i, count in enumerate(hist))

    w0 = 0
    sum0 = 0
    best_t = 128
    max_var = -1.0

    for t in range(256):
        w0 += hist[t]
        if w0 == 0:
            continue
        w1 = total - w0
        if w1 == 0:
            break

        sum0 += t * hist[t]
        mu0 = sum0 / w0
        mu1 = (total_sum - sum0) / w1
        var = w0 * w1 * ((mu0 - mu1) ** 2)

        if var > max_var:
            max_var = var
            best_t = t

    return best_t


def iterative_threshold(hist: list, eps: float = 0.5) -> Tuple[int, int]:
    total = sum(hist)
    t = sum(i * count for i, count in enumerate(hist)) / total
    iters = 0

    for it in range(1, 100):
        iters = it
        split = int(t)
        n1 = sum(hist[:split + 1])
        n2 = sum(hist[split + 1:])

        mu1 = (sum(i * hist[i] for i in range(split + 1)) / n1) if n1 > 0 else 0
        mu2 = (sum(i * hist[i] for i in range(split + 1, 256)) / n2) if n2 > 0 else 255

        t_next = (mu1 + mu2) / 2.0
        if abs(t_next - t) <= eps:
            t = t_next
            break
        t = t_next

    return int(round(t)), iters


def apply_point_ops(gray: Image.Image, brightness: int, contrast: float, gamma: float, invert: bool) -> Tuple[Image.Image, str]:
    gamma = max(0.05, gamma)
    lut = []
    for i in range(256):
        val = 255 - i if invert else i
        val = contrast * (val - 128.0) + 128.0
        val = val + brightness
        val = min(255.0, max(0.0, val))
        val = 255.0 * ((val / 255.0) ** gamma)
        lut.append(min(255, max(0, int(round(val)))))

    res = gray.point(lut)
    desc = f"Δ={brightness:+d}, α={contrast:.1f}, γ={gamma:.2f}" + (" (негатив)" if invert else "")
    return res, desc


def process(img: Image.Image, mode: str, params: dict) -> Dict[str, Any]:
    gray = to_grayscale(img)
    stats_before = get_stats(gray)

    threshold = None
    iters = None

    if mode == "linear_stretch":
        result_img, desc = linear_stretch(gray, robust=False)
    elif mode == "robust_stretch":
        result_img, desc = linear_stretch(gray, robust=True)
    elif mode == "threshold_otsu":
        threshold = otsu_threshold(gray.histogram())
        result_img = gray.point([255 if i >= threshold else 0 for i in range(256)])
        desc = f"Оцу: T = {threshold}"
    elif mode == "threshold_iterative":
        threshold, iters = iterative_threshold(gray.histogram())
        result_img = gray.point([255 if i >= threshold else 0 for i in range(256)])
        desc = f"IsoData: T = {threshold} ({iters} итер.)"
    elif mode == "point":
        b = int(params.get("brightness", 0))
        c = float(params.get("contrast", 1.0))
        g = float(params.get("gamma", 1.0))
        inv = bool(params.get("invert", False))
        result_img, desc = apply_point_ops(gray, b, c, g, inv)
    else:
        result_img = gray
        desc = "Градации серого"

    stats_after = get_stats(result_img)

    return {
        "mode": mode,
        "image": to_base64(result_img),
        "stats_before": stats_before,
        "stats_after": stats_after,
        "threshold": threshold,
        "iterations": iters,
        "desc": desc
    }
