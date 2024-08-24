import cv2
import numpy as np
import os

def calculate_diameter(contour):
    """Calculate the diameter of the gear based on its contour."""
    (x, y), radius = cv2.minEnclosingCircle(contour)
    diameter = 2 * radius
    return diameter

def detect_defects_and_diameter(ideal_image_path, samples_folder_path, output_folder):
    if not os.path.isfile(ideal_image_path):
        print(f"Error: The ideal image file '{ideal_image_path}' does not exist.")
        return

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    ideal_image = cv2.imread(ideal_image_path, cv2.IMREAD_GRAYSCALE)
    if ideal_image is None:
        print(f"Error: Could not open or read the image '{ideal_image_path}'.")
        return
    
    ideal_blur = cv2.GaussianBlur(ideal_image, (5, 5), 0)
    ideal_edges = cv2.Canny(ideal_blur, 30, 100)

    ideal_contours, _ = cv2.findContours(ideal_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ideal_diameter = max(calculate_diameter(contour) for contour in ideal_contours if cv2.contourArea(contour) > 1500)

    sample_image_paths = [os.path.join(samples_folder_path, f) for f in os.listdir(samples_folder_path) if f.endswith('.jpg') or f.endswith('.png')]
    
    for sample_image_path in sample_image_paths:
        sample_image = cv2.imread(sample_image_path, cv2.IMREAD_GRAYSCALE)
        if sample_image is None:
            print(f"Error: Could not open or read the image '{sample_image_path}'.")
            continue
        
        sample_blur = cv2.GaussianBlur(sample_image, (5, 5), 0)
        sample_edges = cv2.Canny(sample_blur, 30, 100)
        
        sample_contours, _ = cv2.findContours(sample_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sample_diameter = max(calculate_diameter(contour) for contour in sample_contours if cv2.contourArea(contour) > 1500)
        
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
            
            # Ensure area is greater than 0 before performing division
            if area > 1500 and aspect_ratio < 1.5:
                broken_teeth_count += 1
            elif area > 0 and area < 1500 and perimeter / area > 0.1:  # Adjust these thresholds based on inspection
                worn_teeth_count += 1

        if abs(sample_diameter - ideal_diameter) < 10:
            diameter_status = "identical"
        elif sample_diameter > ideal_diameter:
            diameter_status = "larger"
        else:
            diameter_status = "smaller"

        print(f"Results for {os.path.basename(sample_image_path)}:")
        print(f"  Diameter Status: {diameter_status}")
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

