import SpriteKit
import SwiftUI

/// A base SKScene class with common game functionality built-in.
///
/// BaseGameScene provides:
/// - Delta time calculation
/// - State machine (playing, paused, gameOver)
/// - Unified input handling
/// - Node management utilities
/// - Common physics setup
///
/// ## Usage
/// ```swift
/// class MyGameScene: BaseGameScene {
///     override func didMove(to view: SKView) {
///         super.didMove(to: view)
///         // Setup your game
///     }
///
///     override func update(deltaTime: TimeInterval) {
///         // Called every frame with delta time
///         movePlayer(by: playerVelocity * deltaTime)
///     }
///
///     override func handleTap(at location: CGPoint) {
///         // Handle tap/click input
///     }
/// }
/// ```
open class BaseGameScene: SKScene {
    // MARK: - State

    /// Current game state
    public enum State {
        case playing
        case paused
        case gameOver
    }

    /// The current state of the game
    public private(set) var state: State = .playing

    /// Current score
    public var score: Int = 0 {
        didSet { onScoreChanged?(score) }
    }

    /// Callback when score changes
    public var onScoreChanged: ((Int) -> Void)?

    /// Callback when state changes
    public var onStateChanged: ((State) -> Void)?

    /// Callback when game ends
    public var onGameOver: ((Int) -> Void)?

    // MARK: - Timing

    /// Time since last frame
    public private(set) var deltaTime: TimeInterval = 0

    /// Total elapsed game time (pauses excluded)
    public private(set) var elapsedTime: TimeInterval = 0

    /// Last frame timestamp
    private var lastUpdateTime: TimeInterval = 0

    // MARK: - Physics

    /// Gravity vector for the scene
    public var gravity: CGVector {
        get { physicsWorld.gravity }
        set { physicsWorld.gravity = newValue }
    }

    // MARK: - Input

    /// Current touch/click locations
    public private(set) var activeTouches: [CGPoint] = []

    /// Whether touch input is currently active
    public var isTouching: Bool { !activeTouches.isEmpty }

    // MARK: - Lifecycle

    open override func didMove(to view: SKView) {
        super.didMove(to: view)
        setupDefaultPhysics()
    }

    private func setupDefaultPhysics() {
        physicsWorld.gravity = CGVector(dx: 0, dy: -9.8)
        physicsWorld.contactDelegate = self
    }

    open override func update(_ currentTime: TimeInterval) {
        // Calculate delta time
        if lastUpdateTime == 0 {
            lastUpdateTime = currentTime
        }
        deltaTime = min(currentTime - lastUpdateTime, 1.0 / 30.0) // Cap at ~30fps minimum
        lastUpdateTime = currentTime

        guard state == .playing else { return }

        elapsedTime += deltaTime

        // Call subclass update with delta time
        update(deltaTime: deltaTime)
    }

    /// Override this instead of update(_:) for frame updates
    open func update(deltaTime: TimeInterval) {
        // Subclasses override this
    }

    // MARK: - State Management

    /// Pauses the game
    public func pause() {
        guard state == .playing else { return }
        state = .paused
        isPaused = true
        onStateChanged?(.paused)
    }

    /// Resumes the game
    public func resume() {
        guard state == .paused else { return }
        state = .playing
        isPaused = false
        // Reset timing to prevent large delta
        lastUpdateTime = 0
        onStateChanged?(.playing)
    }

    /// Ends the game
    public func gameOver() {
        state = .gameOver
        isPaused = true
        onStateChanged?(.gameOver)
        onGameOver?(score)
    }

    /// Resets the game to initial state
    open func reset() {
        score = 0
        elapsedTime = 0
        lastUpdateTime = 0
        state = .playing
        isPaused = false
        onStateChanged?(.playing)
    }

    // MARK: - Input Handling

    #if os(iOS) || os(tvOS)
    open override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard state == .playing else { return }
        for touch in touches {
            let location = touch.location(in: self)
            activeTouches.append(location)
            handleTouchBegan(at: location)
        }
    }

    open override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard state == .playing else { return }
        activeTouches = touches.map { $0.location(in: self) }
        for touch in touches {
            let location = touch.location(in: self)
            handleTouchMoved(to: location)
        }
    }

    open override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        for touch in touches {
            let location = touch.location(in: self)
            if let index = activeTouches.firstIndex(of: location) {
                activeTouches.remove(at: index)
            }
            handleTouchEnded(at: location)
            handleTap(at: location)
        }
    }

    open override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        activeTouches.removeAll()
    }
    #endif

    #if os(macOS)
    open override func mouseDown(with event: NSEvent) {
        guard state == .playing else { return }
        let location = event.location(in: self)
        activeTouches = [location]
        handleTouchBegan(at: location)
    }

    open override func mouseDragged(with event: NSEvent) {
        guard state == .playing else { return }
        let location = event.location(in: self)
        activeTouches = [location]
        handleTouchMoved(to: location)
    }

    open override func mouseUp(with event: NSEvent) {
        let location = event.location(in: self)
        activeTouches.removeAll()
        handleTouchEnded(at: location)
        handleTap(at: location)
    }
    #endif

    // MARK: - Input Override Points

    /// Called when touch/click begins
    open func handleTouchBegan(at location: CGPoint) {
        // Subclasses override
    }

    /// Called when touch/mouse moves
    open func handleTouchMoved(to location: CGPoint) {
        // Subclasses override
    }

    /// Called when touch/click ends
    open func handleTouchEnded(at location: CGPoint) {
        // Subclasses override
    }

    /// Called for tap/click events
    open func handleTap(at location: CGPoint) {
        // Subclasses override
    }

    // MARK: - Node Management

    /// Spawns a node at the given position
    public func spawn(_ node: SKNode, at position: CGPoint) {
        node.position = position
        addChild(node)
    }

    /// Spawns a node at a random position within the scene
    public func spawnRandom(_ node: SKNode) {
        let x = CGFloat.random(in: 0...size.width)
        let y = CGFloat.random(in: 0...size.height)
        spawn(node, at: CGPoint(x: x, y: y))
    }

    /// Removes all nodes with a given name
    public func removeAll(named name: String) {
        enumerateChildNodes(withName: name) { node, _ in
            node.removeFromParent()
        }
    }

    /// Gets all nodes matching a name pattern
    public func nodes(named pattern: String) -> [SKNode] {
        var result: [SKNode] = []
        enumerateChildNodes(withName: pattern) { node, _ in
            result.append(node)
        }
        return result
    }

    // MARK: - Camera Utilities

    /// Creates and sets up a camera node
    public func setupCamera() -> SKCameraNode {
        let cameraNode = SKCameraNode()
        cameraNode.position = CGPoint(x: size.width / 2, y: size.height / 2)
        addChild(cameraNode)
        camera = cameraNode
        return cameraNode
    }

    /// Smoothly moves camera to follow a target
    public func followTarget(_ target: SKNode, smoothing: CGFloat = 0.1) {
        guard let cam = camera else { return }
        let targetPos = target.position
        let newPos = cam.position.lerp(to: targetPos, t: smoothing)
        cam.position = newPos
    }

    // MARK: - Boundary Utilities

    /// Creates edge loop physics boundary around the scene
    public func createSceneBoundary() {
        let boundary = SKPhysicsBody(edgeLoopFrom: frame)
        boundary.configure(category: .wall, collidesWith: .all, contactsWith: .none)
        physicsBody = boundary
    }

    /// Creates a custom rectangular boundary
    public func createBoundary(rect: CGRect) {
        let boundary = SKPhysicsBody(edgeLoopFrom: rect)
        boundary.configure(category: .wall, collidesWith: .all, contactsWith: .none)
        physicsBody = boundary
    }
}

// MARK: - Physics Contact Delegate

extension BaseGameScene: SKPhysicsContactDelegate {
    open func didBegin(_ contact: SKPhysicsContact) {
        handleContact(contact, began: true)
    }

    open func didEnd(_ contact: SKPhysicsContact) {
        handleContact(contact, began: false)
    }

    /// Override this to handle physics contacts
    open func handleContact(_ contact: SKPhysicsContact, began: Bool) {
        // Subclasses override
    }
}

// MARK: - SwiftUI Integration

/// A SwiftUI view that hosts a SpriteKit scene
public struct SpriteKitView<Scene: SKScene>: UIViewRepresentable {
    let scene: Scene

    public init(scene: Scene) {
        self.scene = scene
    }

    public func makeUIView(context: Context) -> SKView {
        let view = SKView()
        view.presentScene(scene)
        view.ignoresSiblingOrder = true

        #if DEBUG
        view.showsFPS = true
        view.showsNodeCount = true
        #endif

        return view
    }

    public func updateUIView(_ uiView: SKView, context: Context) {}
}
