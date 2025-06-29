#!/usr/bin/env python3
"""
Upload Manager for Esoteric Content
Helps manage your manual upload queue
"""

import os
from pathlib import Path
from datetime import datetime

def show_upload_queue():
    """Display all videos ready for upload"""
    upload_dir = Path("esoteric_content_pipeline/ready_to_upload")
    
    if not upload_dir.exists():
        print("❌ No upload queue directory found")
        return []
    
    # Find all video files
    video_files = list(upload_dir.glob("*.mp4"))
    instruction_files = list(upload_dir.glob("*_upload_instructions.txt"))
    
    if not video_files:
        print("✅ Upload queue is empty - no videos waiting")
        return []
    
    print(f"📤 UPLOAD QUEUE ({len(video_files)} videos ready)")
    print("=" * 50)
    
    for i, video_file in enumerate(sorted(video_files), 1):
        # Get file info
        file_size = video_file.stat().st_size / (1024 * 1024)  # MB
        created_time = datetime.fromtimestamp(video_file.stat().st_ctime)
        
        # Find matching instruction file
        instruction_file = None
        video_timestamp = video_file.stem.split('_')[0]
        for inst_file in instruction_files:
            if video_timestamp in inst_file.name:
                instruction_file = inst_file
                break
        
        print(f"{i}. {video_file.name}")
        print(f"   📁 Size: {file_size:.1f} MB")
        print(f"   ⏰ Created: {created_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   📋 Instructions: {'✅' if instruction_file else '❌'}")
        
        if instruction_file:
            # Extract topic from instructions
            try:
                with open(instruction_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('📝 TOPIC:'):
                            topic = line.replace('📝 TOPIC:', '').strip()
                            print(f"   🎯 Topic: {topic}")
                            break
            except:
                pass
        
        print()
    
    return video_files

def show_upload_instructions(video_number=None):
    """Show upload instructions for a specific video"""
    upload_dir = Path("esoteric_content_pipeline/ready_to_upload")
    video_files = sorted(list(upload_dir.glob("*.mp4")))
    
    if not video_files:
        print("❌ No videos in upload queue")
        return
    
    if video_number is None:
        print("📋 Which video do you want instructions for?")
        for i, video_file in enumerate(video_files, 1):
            print(f"{i}. {video_file.name}")
        
        try:
            video_number = int(input("\nEnter video number: "))
        except ValueError:
            print("❌ Invalid number")
            return
    
    if video_number < 1 or video_number > len(video_files):
        print("❌ Invalid video number")
        return
    
    # Find instruction file
    selected_video = video_files[video_number - 1]
    video_timestamp = selected_video.stem.split('_')[0]
    
    instruction_files = list(upload_dir.glob(f"{video_timestamp}_upload_instructions.txt"))
    
    if not instruction_files:
        print(f"❌ No instructions found for {selected_video.name}")
        return
    
    instruction_file = instruction_files[0]
    
    print("\n" + "=" * 60)
    print(f"📋 UPLOAD INSTRUCTIONS FOR: {selected_video.name}")
    print("=" * 60)
    
    try:
        with open(instruction_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"❌ Error reading instructions: {e}")

def mark_as_uploaded(video_number):
    """Mark a video as uploaded and move it to archive"""
    upload_dir = Path("esoteric_content_pipeline/ready_to_upload")
    archive_dir = Path("esoteric_content_pipeline/uploaded_archive")
    archive_dir.mkdir(exist_ok=True)
    
    video_files = sorted(list(upload_dir.glob("*.mp4")))
    
    if not video_files or video_number < 1 or video_number > len(video_files):
        print("❌ Invalid video number")
        return
    
    selected_video = video_files[video_number - 1]
    video_timestamp = selected_video.stem.split('_')[0]
    
    # Move video to archive
    archive_video_path = archive_dir / selected_video.name
    selected_video.rename(archive_video_path)
    
    # Move instruction file if it exists
    instruction_files = list(upload_dir.glob(f"{video_timestamp}_upload_instructions.txt"))
    if instruction_files:
        archive_instruction_path = archive_dir / instruction_files[0].name
        instruction_files[0].rename(archive_instruction_path)
    
    print(f"✅ {selected_video.name} marked as uploaded and archived")

def cleanup_old_files():
    """Clean up files older than 7 days from archive"""
    archive_dir = Path("esoteric_content_pipeline/uploaded_archive")
    
    if not archive_dir.exists():
        print("✅ No archive to clean")
        return
    
    cutoff_time = datetime.now().timestamp() - (7 * 24 * 60 * 60)  # 7 days ago
    cleaned_count = 0
    
    for file_path in archive_dir.iterdir():
        if file_path.stat().st_ctime < cutoff_time:
            file_path.unlink()
            cleaned_count += 1
    
    print(f"🧹 Cleaned {cleaned_count} old files from archive")

def show_stats():
    """Show content creation statistics"""
    base_dir = Path("esoteric_content_pipeline")
    
    # Count files in each directory
    scripts = len(list((base_dir / "scripts").glob("*.txt"))) if (base_dir / "scripts").exists() else 0
    videos = len(list((base_dir / "final_videos").glob("*.mp4"))) if (base_dir / "final_videos").exists() else 0
    ready_uploads = len(list((base_dir / "ready_to_upload").glob("*.mp4"))) if (base_dir / "ready_to_upload").exists() else 0
    archived = len(list((base_dir / "uploaded_archive").glob("*.mp4"))) if (base_dir / "uploaded_archive").exists() else 0
    
    print("📊 CONTENT STATISTICS")
    print("=" * 30)
    print(f"📝 Scripts generated: {scripts}")
    print(f"🎬 Videos created: {videos}")
    print(f"📤 Ready to upload: {ready_uploads}")
    print(f"✅ Uploaded & archived: {archived}")
    print(f"📈 Total content pieces: {scripts}")

def main():
    """Main upload manager interface"""
    print("📤 Esoteric Content Upload Manager")
    print("=" * 40)
    
    while True:
        print("\n🎛️ OPTIONS:")
        print("1. Show upload queue")
        print("2. View upload instructions")
        print("3. Mark video as uploaded")
        print("4. Show statistics")
        print("5. Cleanup old files")
        print("0. Exit")
        
        try:
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                show_upload_queue()
            elif choice == "2":
                show_upload_instructions()
            elif choice == "3":
                video_files = show_upload_queue()
                if video_files:
                    try:
                        video_num = int(input("Enter video number to mark as uploaded: "))
                        mark_as_uploaded(video_num)
                    except ValueError:
                        print("❌ Invalid number")
            elif choice == "4":
                show_stats()
            elif choice == "5":
                cleanup_old_files()
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()