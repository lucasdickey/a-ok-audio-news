from django.core.management.base import BaseCommand
from django.utils import timezone
from digests.models import DailyDigest
import os
import sys

class Command(BaseCommand):
    help = 'Test the v3 agents pipeline with content filtering and validation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date for the test (YYYY-MM-DD format)',
            default=str(timezone.now().date())
        )
        parser.add_argument(
            '--no-editor',
            action='store_true',
            help='Skip the editorial review step'
        )
        parser.add_argument(
            '--save',
            action='store_true',
            help='Save the result to database'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Testing V3 Agents Pipeline (Content Filtering)'))
        self.stdout.write('=' * 60)
        
        # Import the v3 pipeline
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        from agents_pipeline_v3 import generate_episode_v3
        
        # Check API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR('❌ ANTHROPIC_API_KEY not found'))
            return
        
        self.stdout.write(f"✅ API key found: {api_key[:10]}...")
        
        test_date = options['date']
        use_editor = not options['no_editor']
        save_result = options['save']
        
        self.stdout.write(f"\n🔬 Testing V3 pipeline:")
        self.stdout.write(f"   📅 Date: {test_date}")
        self.stdout.write(f"   ⏰ 24-hour constraint: ENABLED")
        self.stdout.write(f"   🧹 Content filtering: ENABLED")
        self.stdout.write(f"   ✅ Validation: ENABLED")
        self.stdout.write(f"   🧠 Editor: {'Enabled' if use_editor else 'Disabled'}")
        self.stdout.write(f"   💾 Save to DB: {'Yes' if save_result else 'No'}")
        
        try:
            self.stdout.write("\n⏳ Running V3 agents pipeline...")
            self.stdout.write("   This may take several minutes due to web searches and validation...")
            
            episode_result = generate_episode_v3(
                date_str=test_date,
                with_editor=use_editor,
                debug=False  # Disable debug to reduce noise
            )
            
            self.stdout.write(self.style.SUCCESS('\n✅ V3 Pipeline completed successfully!'))
            
            # Show detailed validation results
            validations = episode_result.get('validations', {})
            
            self.stdout.write(f"\n📊 VALIDATION RESULTS:")
            for stage, validation in validations.items():
                if validation:
                    status = "✅ PASS" if validation.get('valid', False) else "❌ FAIL"
                    self.stdout.write(f"   {stage.upper()}: {status}")
                    if validation.get('issues'):
                        for issue in validation['issues']:
                            self.stdout.write(f"     - {issue}")
                    
                    self.stdout.write(f"     Stories: {validation.get('story_count', 0)}")
                    self.stdout.write(f"     Citations: {validation.get('citation_count', 0)}")
                    self.stdout.write(f"     Search leakage: {'Yes' if validation.get('has_leakage') else 'No'}")
            
            # Content analysis
            if episode_result.get('script'):
                script_text = episode_result['script']
                self.stdout.write(f"\n🎙️ FINAL SCRIPT ANALYSIS:")
                self.stdout.write(f"   📏 Length: {len(script_text)} chars")
                
                # Format validation
                has_opening = "Hello world" in script_text and "Apes On Knowledge" in script_text
                has_closing = "A-OK Newsbot" in script_text and "signing off" in script_text
                
                self.stdout.write(f"   ✅ Proper opening: {'Yes' if has_opening else 'No'}")
                self.stdout.write(f"   ✅ Proper closing: {'Yes' if has_closing else 'No'}")
                
                # Quality check
                search_leakage = any(indicator in script_text for indicator in [
                    "Let me search", "I'll search for", "Based on the search results"
                ])
                self.stdout.write(f"   🧹 Clean output: {'Yes' if not search_leakage else 'No'}")
                
                self.stdout.write("\n📄 Script Preview (first 500 chars):")
                self.stdout.write("-" * 50)
                preview = script_text[:500] + "..." if len(script_text) > 500 else script_text
                self.stdout.write(preview)
                self.stdout.write("-" * 50)
                
                # Save to database if requested
                if save_result:
                    try:
                        digest, created = DailyDigest.objects.get_or_create(
                            date=test_date,
                            defaults={
                                'summary_text_en': script_text,
                                'summary_text_es': '',
                                'summary_text_fr': '',
                                'summary_text_de': '',
                                'summary_text_ja': '',
                                'audio_file_en': '',
                                'audio_file_es': '',
                                'audio_file_fr': '',
                                'audio_file_de': '',
                                'audio_file_ja': '',
                                'rss_published': False
                            }
                        )
                        
                        if not created:
                            # Update existing
                            digest.summary_text_en = script_text
                            digest.save()
                            self.stdout.write(self.style.SUCCESS(f"✅ Updated existing digest for {test_date}"))
                        else:
                            self.stdout.write(self.style.SUCCESS(f"✅ Created new digest for {test_date}"))
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Failed to save to database: {e}"))
            
            # Calculate overall score
            final_validation = validations.get('final', {})
            if final_validation:
                issues = len(final_validation.get('issues', []))
                has_leakage = final_validation.get('has_leakage', False)
                story_count = final_validation.get('story_count', 0)
                citation_count = final_validation.get('citation_count', 0)
                
                score = 100
                score -= issues * 15  # Deduct for validation issues
                score -= 30 if has_leakage else 0  # Heavy penalty for search leakage
                score -= max(0, (10 - story_count) * 10)  # Penalty for missing stories
                score -= max(0, (5 - citation_count) * 5)  # Penalty for missing citations
                score = max(0, score)
                
                if score >= 80:
                    style = self.style.SUCCESS
                elif score >= 60:
                    style = self.style.WARNING
                else:
                    style = self.style.ERROR
                
                self.stdout.write(style(f'\n🎯 V3 QUALITY SCORE: {score}/100'))
            
            self.stdout.write(self.style.SUCCESS('\n🎉 V3 Test completed successfully!'))
            self.stdout.write("\n📈 V3 IMPROVEMENTS:")
            self.stdout.write("   - Content filtering to prevent search leakage")
            self.stdout.write("   - Real-time validation at each stage")
            self.stdout.write("   - Strict output format requirements")
            self.stdout.write("   - Enhanced citation enforcement")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ V3 Pipeline test failed: {e}'))
            self.stdout.write(self.style.ERROR(f'   Error type: {type(e).__name__}'))
            import traceback
            self.stdout.write(self.style.ERROR(f'   Traceback: {traceback.format_exc()[:500]}')) 