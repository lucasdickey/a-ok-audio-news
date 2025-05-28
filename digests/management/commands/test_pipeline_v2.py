from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import sys

class Command(BaseCommand):
    help = 'Test the v2 agents pipeline with 24-hour constraints and citation requirements'

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

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Testing V2 Agents Pipeline (24-hour constraint)'))
        self.stdout.write('=' * 60)
        
        # Import the v2 pipeline
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        from agents_pipeline_v2 import generate_episode_v2
        
        # Check API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR('❌ ANTHROPIC_API_KEY not found'))
            return
        
        self.stdout.write(f"✅ API key found: {api_key[:10]}...")
        
        test_date = options['date']
        use_editor = not options['no_editor']
        
        self.stdout.write(f"\n🔬 Testing V2 pipeline:")
        self.stdout.write(f"   📅 Date: {test_date}")
        self.stdout.write(f"   ⏰ 24-hour constraint: ENABLED")
        self.stdout.write(f"   📰 Citation requirements: ENHANCED")
        self.stdout.write(f"   🧠 Editor: {'Enabled' if use_editor else 'Disabled'}")
        
        try:
            self.stdout.write("\n⏳ Running V2 agents pipeline...")
            self.stdout.write("   This may take several minutes due to multiple web searches...")
            
            episode_result = generate_episode_v2(
                date_str=test_date,
                with_editor=use_editor,
                debug=False  # Disable debug to reduce noise in command output
            )
            
            self.stdout.write(self.style.SUCCESS('\n✅ V2 Pipeline completed successfully!'))
            
            # Show results with enhanced analysis
            if episode_result.get('research'):
                research_text = episode_result['research']
                self.stdout.write(f"🔍 Research: {len(research_text)} chars")
                
                # Count apparent citations in research
                citation_indicators = ['reports', 'according to', 'announced', 'published', 'revealed']
                citation_count = sum(research_text.lower().count(indicator) for indicator in citation_indicators)
                self.stdout.write(f"   📰 Apparent citations found: {citation_count}")
                
            if episode_result.get('summary'):
                summary_text = episode_result['summary']
                self.stdout.write(f"📝 Summary: {len(summary_text)} chars")
                
                # Count stories in summary
                story_count = summary_text.count('STORY')
                self.stdout.write(f"   📊 Stories identified: {story_count}")
                
            if episode_result.get('script'):
                script_text = episode_result['script']
                self.stdout.write(f"🎙️ Script: {len(script_text)} chars")
                
                # Analyze script quality
                has_opening = "Hello world" in script_text and "Apes On Knowledge" in script_text
                has_closing = "A-OK Newsbot" in script_text and "signing off" in script_text
                citation_count = script_text.count("reports") + script_text.count("according to")
                
                self.stdout.write(f"   ✅ Proper opening: {'Yes' if has_opening else 'No'}")
                self.stdout.write(f"   ✅ Proper closing: {'Yes' if has_closing else 'No'}")
                self.stdout.write(f"   📰 Source citations: {citation_count}")
                
                self.stdout.write("\n📄 Script Preview (first 400 chars):")
                self.stdout.write("-" * 50)
                preview = script_text[:400] + "..." if len(script_text) > 400 else script_text
                self.stdout.write(preview)
                self.stdout.write("-" * 50)
            
            self.stdout.write(self.style.SUCCESS('\n🎉 V2 Test completed successfully!'))
            self.stdout.write("\n📊 Quality Metrics:")
            self.stdout.write("   - 24-hour constraint enforcement")
            self.stdout.write("   - Enhanced citation requirements")
            self.stdout.write("   - Listener trust emphasis")
            self.stdout.write("   - Verifiable source requirements")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ V2 Pipeline test failed: {e}'))
            self.stdout.write(self.style.ERROR(f'   Error type: {type(e).__name__}'))
            import traceback
            self.stdout.write(self.style.ERROR(f'   Traceback: {traceback.format_exc()[:500]}')) 