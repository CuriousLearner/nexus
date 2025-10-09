# -*- coding: utf-8 -*-
# Standard Library
import os
from io import BytesIO

# Third Party Stuff
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


# Platform-specific image requirements
PLATFORM_SPECS = {
    'fb': {
        'max_width': 2048,
        'max_height': 2048,
        'aspect_ratios': [(1, 1), (16, 9), (9, 16)],
        'max_size_mb': 8,
    },
    'twitter': {
        'max_width': 4096,
        'max_height': 4096,
        'aspect_ratios': [(16, 9), (1, 1), (4, 3)],
        'max_size_mb': 5,
    },
    'instagram': {
        'max_width': 1080,
        'max_height': 1350,
        'aspect_ratios': [(1, 1), (4, 5), (16, 9)],
        'max_size_mb': 8,
    },
    'linkedin': {
        'max_width': 1200,
        'max_height': 627,
        'aspect_ratios': [(1.91, 1)],
        'max_size_mb': 5,
    },
    'threads': {
        'max_width': 1080,
        'max_height': 1350,
        'aspect_ratios': [(1, 1), (4, 5), (16, 9)],
        'max_size_mb': 8,
    },
}


def optimize_image_for_platform(image_file, platform='fb', quality=85):
    """Optimize image for specific platform requirements

    :param image_file: Django ImageField or file path
    :param platform: Platform to optimize for (fb, twitter, instagram, linkedin, threads)
    :param quality: JPEG quality (1-100)
    :returns: Optimized image file
    """
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS['fb'])

    # Open image
    img = Image.open(image_file)

    # Convert RGBA to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background

    # Resize if larger than max dimensions
    max_width = specs['max_width']
    max_height = specs['max_height']

    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    # Save optimized image to BytesIO
    output = BytesIO()
    img_format = 'JPEG'

    # Determine format from original file
    if hasattr(image_file, 'name'):
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext in ['.png']:
            img_format = 'PNG'

    img.save(output, format=img_format, quality=quality, optimize=True)
    output.seek(0)

    # Check file size
    max_size_bytes = specs['max_size_mb'] * 1024 * 1024
    if output.getbuffer().nbytes > max_size_bytes and quality > 50:
        # Reduce quality if file is too large
        return optimize_image_for_platform(image_file, platform, quality - 10)

    # Create new InMemoryUploadedFile
    if hasattr(image_file, 'name'):
        filename = image_file.name
    else:
        filename = 'optimized_image.jpg'

    return InMemoryUploadedFile(
        output,
        'ImageField',
        filename,
        f'image/{img_format.lower()}',
        output.getbuffer().nbytes,
        None
    )


def optimize_image_for_all_platforms(image_file):
    """Generate optimized versions for all platforms

    :param image_file: Django ImageField or file path
    :returns: Dict with optimized images for each platform
    """
    optimized = {}
    for platform in PLATFORM_SPECS.keys():
        optimized[platform] = optimize_image_for_platform(image_file, platform)
    return optimized


def get_image_info(image_file):
    """Get information about an image

    :param image_file: Django ImageField or file path
    :returns: Dict with image info
    """
    img = Image.open(image_file)
    return {
        'width': img.width,
        'height': img.height,
        'format': img.format,
        'mode': img.mode,
        'aspect_ratio': round(img.width / img.height, 2),
    }


def validate_image_for_platform(image_file, platform):
    """Check if image meets platform requirements

    :param image_file: Django ImageField or file path
    :param platform: Platform to validate for
    :returns: Tuple (is_valid, error_message)
    """
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS['fb'])
    info = get_image_info(image_file)

    # Check dimensions
    if info['width'] > specs['max_width'] or info['height'] > specs['max_height']:
        return False, f"Image too large. Max dimensions: {specs['max_width']}x{specs['max_height']}"

    # Check file size
    image_file.seek(0, os.SEEK_END)
    file_size_mb = image_file.tell() / (1024 * 1024)
    image_file.seek(0)

    if file_size_mb > specs['max_size_mb']:
        return False, f"File size too large. Max: {specs['max_size_mb']}MB"

    return True, "Image valid"
