from app.use_cases.analyze_assets import AnalyzeAssetsUseCase

if __name__ == "__main__":
    use_case = AnalyzeAssetsUseCase()
    use_case.execute()