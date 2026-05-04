import os
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Gera documentação completa do projeto para Obsidian"

    def handle(self, *args, **kwargs):
        base_path = os.path.abspath("../aprendix-docs")

        os.makedirs(base_path, exist_ok=True)

        # Estrutura base
        pastas = [
            "00_Arquitetura",
            "01_Apps",
            "02_Fluxos",
            "03_Auditoria",
            "04_Diagramas",
        ]

        for pasta in pastas:
            os.makedirs(os.path.join(base_path, pasta), exist_ok=True)

        self.stdout.write(self.style.SUCCESS("📁 Estrutura base criada"))

        # ===============================
        # GERA DOCUMENTAÇÃO POR APP
        # ===============================
        for app in apps.get_app_configs():
            app_name = app.label
            app_path = os.path.join(base_path, "01_Apps", app_name)

            os.makedirs(app_path, exist_ok=True)

            models = app.get_models()

            for model in models:
                model_name = model.__name__
                file_path = os.path.join(app_path, f"{model_name}.md")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# 📦 {model_name}\n\n")
                    f.write(f"App: **{app_name}**\n\n")

                    f.write("## 🔗 Relacionamentos\n\n")

                    for field in model._meta.get_fields():
                        if field.is_relation and field.related_model:
                            related = field.related_model.__name__
                            f.write(f"- {field.name} → [[{related}]]\n")

                    f.write("\n## 📊 Campos\n\n")

                    for field in model._meta.fields:
                        f.write(f"- {field.name} ({field.get_internal_type()})\n")

            self.stdout.write(self.style.SUCCESS(f"✔ App documentado: {app_name}"))

        # ===============================
        # GERA ARQUITETURA
        # ===============================
        arq_file = os.path.join(base_path, "00_Arquitetura", "grafo_models.md")

        with open(arq_file, "w", encoding="utf-8") as f:
            f.write("# 📊 Grafo dos Models\n\n")
            f.write("![[../04_Diagramas/modelos.png]]\n\n")
            f.write("## 🔎 Visão Geral\n")
            f.write("Estrutura automática gerada a partir do Django.\n")

        self.stdout.write(self.style.SUCCESS("📊 Arquitetura criada"))

        self.stdout.write(self.style.SUCCESS("\n🚀 Vault Obsidian gerado com sucesso!"))