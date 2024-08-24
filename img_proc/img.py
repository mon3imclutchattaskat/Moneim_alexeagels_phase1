import cv2
import numpy as np
import os

def calculate_diameter(contour):
    """Calculate the diameter of the gear based on its contour."""
    (x, y), radius = cv2.minEnclosingCircle(contour)
    return 2 * radius

def detect_inner_opening(contour):
    """Detect and calculate the area of the inner opening of the gear."""
    (x, y), radius = cv2.minEnclosingCircle(contour)
    return np.pi * (radius ** 2)

def align_images(ideal_image, sample_image):
    """Align the sample image to the ideal image using geometric transformations."""
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(ideal_image, None)
    kp2, des2 = orb.detectAndCompute(sample_image, None)
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    
    if len(matches) >= 4:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        aligned_image = cv2.warpPerspective(sample_image, matrix, (ideal_image.shape[1], ideal_image.shape[0]))
        return aligned_image
    else:
        print("Not enough matches found for alignment.")
        return sample_image

def detect_defects_and_diameter(ideal_image_path, samples_folder_path, output_folder):
    # Load the ideal image and convert it to grayscale
    ideal_image = cv2.imread(ideal_image_path, cv2.IMREAD_GRAYSCALE)
    if ideal_image is None:
        print(f"Error: Could not open or read the image '{ideal_image_path}'.")
        return
    
    ideal_blur = cv2.GaussianBlur(ideal_image, (5, 5), 0)
    ideal_edges = cv2.Canny(ideal_blur, 30, 100)
    
    ideal_contours, _ = cv2.findContours(ideal_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ideal_diameter = max(calculate_diameter(contour) for contour in ideal_contours if cv2.contourArea(contour) > 1500)
    ideal_inner_area = max(detect_inner_opening(contour) for contour in ideal_contours if cv2.contourArea(contour) > 1500)
    
    os.makedirs(output_folder, exist_ok=True)
    sample_image_paths = [os.path.join(samples_folder_path, f) for f in os.listdir(samples_folder_path) if f.endswith('.jpg') or f.endswith('.png')]
    
    for sample_image_path in sample_image_paths:
        sample_image = cv2.imread(sample_image_path, cv2.IMREAD_GRAYSCALE)
        if sample_image is None:
            print(f"Error: Could not open or read the image '{sample_image_path}'.")
            continue
        
        # Align the sample image with the ideal image
        aligned_image = align_images(ideal_image, sample_image)
        
        # Process the aligned image
        sample_blur = cv2.GaussianBlur(aligned_image, (5, 5), 0)
        sample_edges = cv2.Canny(sample_blur, 30, 100)
        
        sample_contours, _ = cv2.findContours(sample_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sample_diameter = max(calculate_diameter(contour) for contour in sample_contours if cv2.contourArea(contour) > 1500)
        sample_inner_area = max(detect_inner_opening(contour) for contour in sample_contours if cv2.contourArea(contour) > 1500)
        
        diff_edges = cv2.bitwise_xor(ideal_edges, sample_edges)
        diff_contours, _ = cv2.findContours(diff_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        broken_teeth_count = 0
        worn_teeth_count = 0

        for contour in diff_contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            aspect_ratio = 0
            
            x, y, w, h = cv2.boundingRect(contour)
            if h != 0:
                aspect_ratio = float(w) / h
            
            if area > 1500 and aspect_ratio < 1.5:
                broken_teeth_count += 1
            elif area > 0 and area < 1500 and perimeter / area > 0.1:
                worn_teeth_count += 1

        diameter_status = "identical" if abs(sample_diameter - ideal_diameter) < 10 else ("larger" if sample_diameter > ideal_diameter else "smaller")
        inner_opening_status = "identical" if abs(sample_inner_area - ideal_inner_area) < 100 else "different"
        
        print(f"Results for {os.path.basename(sample_image_path)}:")
        print(f"  Diameter Status: {diameter_status}")
        print(f"  Inner Opening Status: {inner_opening_status}")
        print(f"  Broken Teeth Count: {broken_teeth_count}")
        print(f"  Worn Teeth Count: {worn_teeth_count}")
        
        # Save the processed images to the output folder
        output_image_path = os.path.join(output_folder, os.path.basename(sample_image_path))
        cv2.imwrite(output_image_path, sample_edges)

# Define paths to the ideal image and samples folder
ideal_image_path = 'samples/ideal.jpg'
samples_folder_path = 'samples'
output_folder = 'extracted_samples'

# Run the defect detection and diameter comparison
detect_defects_and_diameter(ideal_image_path, samples_folder_path, output_folder)

