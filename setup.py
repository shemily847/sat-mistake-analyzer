# setup_project.py

import os
import json

# 디렉토리 및 파일 구조 정의
project_structure = {
    'project': {
        'scripts': {
            'data_analysis.py': '',
            'explanations.py': '',
            'study_plan.py': '',
            'export_report.py': '',
        },
        'data': {
            'mistakes_data.csv': '',  # 기본 내용 없음
        },
        'app.py': '',
        'history.json': {}  # 빈 JSON 객체로 초기화
    }
}

# 구조 생성 함수
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # 폴더
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:  # 파일
            with open(path, 'w', encoding='utf-8') as f:
                if isinstance(content, dict):  # JSON 파일
                    json.dump(content, f, indent=4)
                else:
                    f.write(content)

# 실행
if __name__ == "__main__":
    base_dir = os.getcwd()  # 현재 디렉토리에 생성
    create_structure(base_dir, project_structure)
    print("✅ 프로젝트 구조가 성공적으로 생성되었습니다.")
