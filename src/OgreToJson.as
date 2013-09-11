package {
	import flash.desktop.ClipboardFormats;
	import flash.desktop.NativeDragManager;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.NativeDragEvent;
	import flash.filesystem.File;
	import flash.filesystem.FileMode;
	import flash.filesystem.FileStream;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.utils.Dictionary;
	
	import threeshooter.Parser;

	[SWF(width = "550", height = "400")]
	public class OgreToJson extends Sprite {

		private var _msg:TextField;
		private var _dragTarget:Sprite;

		public function OgreToJson() {
			addEventListener(Event.ADDED_TO_STAGE, addedToStageHandler);
		}

		private function readString(file:File):String {
			var fileStream:FileStream = new FileStream();
			fileStream.open(file, FileMode.READ);
			var str:String = fileStream.readUTFBytes(fileStream.bytesAvailable);
			fileStream.close();
			return str;
		}

		private function readXml(file:File):XML {
			return new XML(readString(file));
		}

		private function writeJson(mesh:Object, name:String):void {
			var destFile:File = File.applicationDirectory.resolvePath(name + ".json");
			var fileStream:FileStream = new FileStream();
			fileStream.open(new File(destFile.nativePath), FileMode.WRITE);
			fileStream.writeUTFBytes(JSON.stringify(mesh));
			fileStream.close();

			_msg.appendText("Export: " + destFile.nativePath + "\n");
		}

		protected function addedToStageHandler(event:Event):void {

			removeEventListener(Event.ADDED_TO_STAGE, addedToStageHandler);

			var stageWidth:int = 550;
			var stageHeight:int = 400;
			var dragCell:int = 100;

			_dragTarget = new Sprite();
			_dragTarget.graphics.beginFill(0xffffff * Math.random());
			_dragTarget.graphics.drawRoundRect(stageWidth / 2 - dragCell / 2, stageHeight / 2 - dragCell / 2, dragCell, dragCell, 5, 5);
			_dragTarget.graphics.endFill();
			addChild(_dragTarget);

			_msg = new TextField();
			_msg.width = 550;
			_msg.height = 400;
			_msg.autoSize = TextFieldAutoSize.LEFT;
			_msg.multiline = true;
			_msg.wordWrap = true;
			addChild(_msg);

			_dragTarget.addEventListener(NativeDragEvent.NATIVE_DRAG_ENTER, dragEnterHandler);
			_dragTarget.addEventListener(NativeDragEvent.NATIVE_DRAG_DROP, dragDropHandler);
		}

		protected function dragDropHandler(event:NativeDragEvent):void {
			var dropFiles:Array = event.clipboard.getData(ClipboardFormats.FILE_LIST_FORMAT) as Array;
			for each (var file:File in dropFiles) {
				var materials:Dictionary = Parser.parseMaterials(readString(new File(file.nativePath.replace(".MESH." + file.extension, ".MATERIAL"))));
				writeJson(Parser.parseMesh(readXml(file), materials), file.name.replace("." + file.extension, ""));
			}
		}

		protected function dragEnterHandler(event:NativeDragEvent):void {
			NativeDragManager.acceptDragDrop(_dragTarget);
		}
	}
}
