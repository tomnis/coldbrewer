import { Heading, Flex } from "@chakra-ui/react";

const Header = () => {
  return (
    <Flex
      as="nav"
      align="center"
      justify="space-between"
      wrap="wrap"
      padding="0.75rem 1rem"
      bg="#0a0a0a"
      borderBottom="2px solid #33ff33"
      width="100%"
      position="fixed"
      top="0"
      left="0"
      right="0"
      zIndex="1000"
      boxShadow="0 0 10px #33ff33"
    >
      <Flex align="center" as="nav" mr={5}>
        <Heading 
          as="h1" 
          size="md" 
          className="terminal-glow"
          fontFamily="'VT323', 'Courier New', Courier, monospace"
        >
          COLDBREWER v1.0
        </Heading>
      </Flex>
      <Flex align="center">
        <span className="terminal-glow" style={{ fontSize: '0.9em' }}>
          [System Online]
        </span>
      </Flex>
    </Flex>
  );
};

export default Header;
