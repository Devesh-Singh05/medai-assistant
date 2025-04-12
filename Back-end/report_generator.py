import os
import json
import time
import logging
import google.generativeai as genai
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyArDoTpv6b4oCx1u2l_HmQfnPkhE4jI5JE')
genai.configure(api_key=GEMINI_API_KEY)

def generate_report(patient_info, scan_results):
    """Generate a detailed medical report using Gemini API"""
    try:
        # Create a prompt for the medical report
        prompt = f"""
        Generate a detailed professional medical report for a brain tumor MRI scan in this format:

        Patient Information:
        - Name: {patient_info.get('name', 'N/A')}
        - ID: {patient_info.get('id', 'N/A')}
        - Date: {datetime.now().strftime('%B %d, %Y')}

        Technical Details:
        - Number of Detected Tumors: {scan_results.get('numDetections', 0)}
        - Detection Confidence: {', '.join(f'{conf*100:.1f}%' for conf in scan_results.get('confidences', []))}

        Based on these details, provide a thorough analysis following this structure:

        EXAMINATION:
        [Brief description of the MRI scan performed]

        FINDINGS:
        - Location(s) of detected abnormalities
        - Size and characteristics of each tumor
        - Impact on surrounding brain tissue

        IMPRESSION:
        [Summary of key findings and their clinical significance]

        RECOMMENDATIONS:
        [Specific next steps for patient care]

        Please be thorough but concise, using relevant medical terminology while maintaining clarity.
        Note: Use bullet points where appropriate for clarity.
        """

        # Generate report using Gemini
        model = genai.GenerativeModel('gemini-1.0-pro')
        response = model.generate_content(prompt)
        
        # Format the report
        report = {
            'patientInfo': {
                'name': patient_info.get('name', 'N/A'),
                'id': patient_info.get('id', 'N/A'),
                'date': datetime.now().strftime('%Y-%m-%d'),
            },
            'scanResults': {
                'numDetections': scan_results.get('numDetections', 0),
                'confidences': scan_results.get('confidences', []),
            },
            'report': response.text,
            'generatedAt': datetime.now().isoformat()
        }
        
        # Save report to file
        report_dir = Path('reports')
        report_dir.mkdir(exist_ok=True)
        
        report_path = report_dir / f"report_{patient_info.get('id')}_{int(time.time())}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logging.info(f"Report generated and saved to {report_path}")
        return report
        
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        raise

if __name__ == "__main__":
    # Test report generation
    test_data = {
        'patientInfo': {
            'name': 'Test Patient',
            'id': 'TP001',
        },
        'scanResults': {
            'numDetections': 2,
            'confidences': [0.92, 0.85],
        }
    }
    
    try:
        report = generate_report(test_data['patientInfo'], test_data['scanResults'])
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(f"Error in test: {str(e)}")
